// Jenkinsfile — "Build at AI Speed" demo pipeline
//
// Act 1 (Governance): if the changeset touches a sensitive path (auth,
// payments), the pipeline pauses for a named human approval before
// continuing. This is the control point — it doesn't matter whether a
// human or an AI coding agent authored the change.
//
// Act 2 (Triage & Speed): CloudBees Smart Tests records the build/session,
// runs a predictive subset (or full suite on the nightly), and every test
// result is sent back to Smart Tests so failures can be clustered by root
// cause instead of read one-by-one.
//
// NOTE ON AGENTS: this controller's "default" pod template has git but no
// Python and no package manager. Rather than a second, separate pod (which
// caused workspace-ownership/permission conflicts), this Jenkinsfile
// inherits the existing "default" template and adds a python container
// alongside it — one pod, one shared workspace. Checkout/gate steps run in
// the default container (unwrapped); Python/Smart Tests steps are wrapped
// in container('python').
//
// NOTE ON THE SMART TESTS CLI: the installable PyPI package is named
// smart-tests-cli (the CLI binary it installs is called smart-tests).
// The pytest subset workflow requires generating a test list via
// `pytest --collect-only -q` first, then piping that into
// `smart-tests subset pytest` — see:
// https://docs.cloudbees.com/docs/cloudbees-smart-tests/latest/send-data-to-smart-tests/subset/subset-with-the-smart-tests-cli

pipeline {
    agent {
        kubernetes {
            inheritFrom 'default'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.13-slim
    command:
    - cat
    tty: true
'''
        }
    }

    environment {
        // Set this as a Jenkins credential (Secret text) named
        // smart-tests-token pointing at your CloudBees Smart Tests API key.
        SMART_TESTS_TOKEN = credentials('smart-tests-token')
        BUILD_NAME = "${env.JOB_NAME.replace('/', '-').replace('%2F', '-')}-${env.BUILD_NUMBER}"

        // DEMO-ONLY knobs (see tests/conftest.py): simulate realistic test
        // durations so a 58-test suite feels like a real CI run instead of
        // finishing in 0.1s, and so Predictive Test Selection has something
        // real to save time on. Tune these numbers directly if the live
        // pacing feels off in rehearsal. Set both to 0 to disable entirely.
        DEMO_TEST_DELAY_SECONDS = "0.35"
        DEMO_SLOW_TEST_EXTRA_SECONDS = "2.5"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git fetch origin main:refs/remotes/origin/main --depth=50 || true'
            }
        }

        stage('Governance Gate — Sensitive Path Check') {
            steps {
                script {
                    def isSensitive = sh(
                        script: "bash scripts/check_sensitive_paths.sh origin/main HEAD",
                        returnStatus: true
                    ) == 0

                    if (isSensitive) {
                        echo "⚠️  This change touches a sensitive path (auth/payments)."
                        echo "Routing for required approval before this can proceed — "
                        echo "regardless of whether a human or an AI coding assistant authored it."
                        // Requires the approve-authenticated-user or a named
                        // approver group. Replace 'platform-team' with a real
                        // Jenkins group/user for the live demo.
                        timeout(time: 15, unit: 'MINUTES') {
                            input message: "Approve change to authentication/payment logic?",
                                  submitter: 'platform-team',
                                  ok: 'Approve'
                        }
                        echo "✅ Approved by human reviewer — audit trail recorded in this build's history."
                    } else {
                        echo "No sensitive paths touched — proceeding without manual gate."
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh '''
                        apt-get update && apt-get install -y --no-install-recommends default-jre-headless git
                        rm -rf /var/lib/apt/lists/*
                        git config --global --add safe.directory '*'

                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt

                        # CloudBees Smart Tests CLI — package name is
                        # smart-tests-cli; the executable it installs is
                        # called smart-tests.
                        pip install --upgrade smart-tests-cli
                    '''
                }
            }
        }

        stage('Smart Tests — Record Build & Session') {
            steps {
                container('python') {
                    sh '''
                        . .venv/bin/activate
                        smart-tests verify || true

                        smart-tests record build \
                            --build "${BUILD_NAME}" \
                            --source repo=.

                        smart-tests record session \
                            --build "${BUILD_NAME}" \
                            --test-suite "pytest-suite" > .smart_tests_session.txt
                    '''
                }
            }
        }

        stage('Predictive Test Selection') {
            when { not { branch 'nightly' } }
            steps {
                container('python') {
                    sh '''
                        . .venv/bin/activate
                        SESSION=$(cat .smart_tests_session.txt)

                        # Generate the full test list pytest would normally
                        # run, without running it.
                        pytest --collect-only -q tests/ > test_list.txt

                        # Pipe that list in to get back a subset.
                        # (Observation mode was tried and abandoned here —
                        # CloudBees CLI v2.12.5 rejects --observation on
                        # `smart-tests subset` outright, contradicting the
                        # docs. Reported to CloudBees support.)
                        cat test_list.txt | smart-tests subset pytest \
                            --session "${SESSION}" \
                            --confidence 90% > subset.txt

                        echo "Selected subset:"
                        cat subset.txt
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                container('python') {
                    sh '''
                        . .venv/bin/activate
                        SESSION=$(cat .smart_tests_session.txt)

                        if [ "${BRANCH_NAME}" = "nightly" ]; then
                            echo "Nightly build — running full suite."
                            python3 -m pytest tests/ --junit-xml=junit.xml || true
                        else
                            echo "Feature branch — running predictive subset."
                            python3 -m pytest --junit-xml=junit.xml $(cat subset.txt) || true
                        fi

                        smart-tests record tests \
                            --session "${SESSION}" \
                            pytest junit.xml
                    '''
                }
                junit allowEmptyResults: true, testResults: 'junit.xml'
            }
        }
    }
}
