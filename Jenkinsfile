import java.text.SimpleDateFormat
node('vmagent') {
    def dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss")
    def date = new Date()
    def output = dateFormat.format(date)

    def succ = true
    def err = ""
    try {
        stage('Clone repository') {
            /* Let's make sure we have the repository cloned to our workspace */
            checkout scm
        }

        stage('Build image') {
            /* This builds the actual image; synonymous to
            * docker build on the command line */
            sh("./build-robertalab-systemd.sh ${output}")
        }

        stage('Test image') {
            /* Ideally, we would run a test framework against our image.
            * For this example, we're using a Volkswagen-type approach ;-) */
        }

        stage('Push image') {
            /* Finally, we'll push the image with two tags:
            * First, the incremental build number from Jenkins
            * Second, the 'latest' tag.
            * Pushing multiple tags is cheap, as all the layers are reused. */
            sh("azcopy \
                --source ${output} \
                --destination https://csdistg.blob.core.windows.net/robertalab-service/${output} \
                --dest-key vv2ZKUmod9oqdKBI7oWnMcPcd5HP0S6VIva8U9QQL/s6SLG1i55la6dKV7qLeMiX6FyxIQFTldGeyOeDCE7JsQ== \
                --recursive")
        }
    } catch (error) {
        succ = false
        err = "error: ${error}"
    } finally {
        notifyStatus(succ, err)
    }
    
}

def notifyStatus(success, error){
    def label = success? "SUCCESS":"FAILED"
    mail (to: 'tiantiaw@microsoft.com',
        subject: "Job '${env.JOB_NAME}' (${env.BUILD_NUMBER}) is ${label}",
        body: "msg: ${error}");
}
