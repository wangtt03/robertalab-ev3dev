podTemplate(label: 'robertalab-service-pod', containers: [
    containerTemplate(name: 'docker', image: 'docker:17.06.0-dind', privileged: true, ttyEnabled: true),
    containerTemplate(name: 'azcopy', image: 'glueckkanja/ci-deploy-linux-azcopy:1.4.1', ttyEnabled: true),
  ]) {
    node('robertalab-service-pod') {
        import java.text.SimpleDateFormat
        def dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss")
        def date = new Date()
        def output = dateFormat.format(date)

        stage("Build"){
            container("docker"){
                stage('Clone repository') {
                    /* Let's make sure we have the repository cloned to our workspace */
                    checkout scm
                }

                stage('Build image') {
                    /* This builds the actual image; synonymous to
                    * docker build on the command line */
                    sh("echo creating output dir: ${output}")
                    sh("./build-robertalab-systemd.sh ${output}")
                }

                stage('Test image') {
                    /* Ideally, we would run a test framework against our image.
                    * For this example, we're using a Volkswagen-type approach ;-) */
                }

            }
        }

        stage('Upload') {
            /* Ideally, we would run a test framework against our image.
            * For this example, we're using a Volkswagen-type approach ;-) */
            container("azcopy"){
                stage("upload"){
                    sh("azcopy \
                        --source ${output} \
                        --destination https://csdistg.blob.core.windows.net/robertalab-service/${output} \
                        --dest-key vv2ZKUmod9oqdKBI7oWnMcPcd5HP0S6VIva8U9QQL/s6SLG1i55la6dKV7qLeMiX6FyxIQFTldGeyOeDCE7JsQ== \
                        --recursive")
                }
            }
        }
    }
}