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

pipeline {
    agent any

    environment {
        // Set this as a Jenkins credential (Secret text) named
        // SMART_TESTS_TOKEN pointing at your CloudBees Smart Tests API key.
        SMART_TESTS_TOKEN = credentials('smart-tests-token')
        BUILD_NAME = "${env.JOB_NAME}-${env.BUILD_NUMBER}"
    }


    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git fetch origin main --depth=50 || true'
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
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # CloudBees Smart Tests CLI (Python package)
                    pip install --upgrade smart-tests
                '''
            }
        }

        stage('Smart Tests — Record Build & Session') {
            steps {
                sh '''
                    . .venv/bin/activate
                    smart-tests verify || true

                    smart-tests record build \
                        --build "${BUILD_NAME}" \
                        --branch "${BRANCH_NAME}" \
                        --source .

                    smart-tests record session \
                        --build "${BUILD_NAME}" \
                        --test-suite "pytest-suite" > .smart_tests_session.txt
                '''
            }
        }

        stage('Predictive Test Selection') {
            when { not { branch 'nightly' } }
            steps {
                sh '''
                    . .venv/bin/activate
                    SESSION=$(cat .smart_tests_session.txt)

                    smart-tests subset pytest \
                        --session "${SESSION}" \
                        --confidence 90% \
                        tests/ > subset.txt

                    echo "Selected subset:"
                    cat subset.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    SESSION=$(cat .smart_tests_session.txt)

                    if [ "${BRANCH_NAME}" = "nightly" ]; then
                        echo "Nightly build — running full suite."
                        python3 -m pytest tests/ --junitxml=junit.xml || true
                    else
                        echo "Feature branch — running predictive subset."
                        python3 -m pytest $(cat subset.txt | tr '\\n' ' ') --junitxml=junit.xml || true
                    fi

                    smart-tests record tests pytest \
                        --session "${SESSION}" \
                        junit.xml
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'junit.xml'
        }
    }
}
