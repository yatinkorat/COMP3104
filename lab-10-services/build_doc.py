"""Build the Lab 10 submission (.docx) from the screenshots in ./screenshots."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).parent
SHOTS = ROOT / "screenshots"
OUT = ROOT / "Lab10-Services-Docker-Kubernetes-Submission.docx"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, side, Inches(0.6))
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)
IMG_W = Inches(7.2)


def para(text, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    return p


def commands(*cmds):
    p = doc.add_paragraph()
    p.add_run("Command:").bold = True
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = True
    for c in cmds:
        q = doc.add_paragraph()
        q.paragraph_format.space_after = Pt(0)
        q.paragraph_format.keep_with_next = True
        q.paragraph_format.left_indent = Inches(0.25)
        r = q.add_run(c)
        r.font.name = "Consolas"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def shot(name, caption):
    # image and caption share one paragraph so they never split across pages
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(SHOTS / name), width=IMG_W)
    p.add_run().add_break()
    c = p.add_run(caption)
    c.italic = True
    c.font.size = Pt(9)


doc.add_heading("Class Exercise 10 – Services with Docker and Kubernetes Deployment", level=0)
para("Name: Yatin Korat")
para("Student ID: 101560107")
para("Date: November 26, 2026")
para("Docker Hub repository: https://hub.docker.com/r/yatinkorat/hellodocker")
para(
    "In this lab I pushed the hellodocker image I built in the last lab to Docker Hub, and then deployed it on "
    "Minikube with a Kubernetes Deployment (3 replicas), a NodePort Service and a Redis Deployment/Service. "
    "All commands were run in Windows PowerShell on my laptop (Docker Desktop 29.8.2, Minikube with the Docker driver)."
)

# ---------------- PART I ----------------
doc.add_heading("PART I – Pushing the Docker image to Docker Hub after tagging", level=1)

doc.add_heading("1. Log in to Docker Hub", level=2)
para(
    "I created a free Docker Hub account with the username yatinkorat and signed in to Docker Desktop. "
    "Running docker login uses the saved credentials and prints Login Succeeded."
)
commands("docker login")
shot("01-docker-login.png", "Figure 1 – docker login succeeded as yatinkorat")

doc.add_heading("2. Find the image built in the last lab", level=2)
para("The hellodocker:latest image from Lab 09 is still on my machine. Its image ID is 9837e200811d.")
commands("docker images hellodocker")
shot("02-docker-images-local.png", "Figure 2 – local hellodocker image")

doc.add_heading("3. Tag the image for Docker Hub", level=2)
para(
    "Docker Hub uses the naming convention username/repository:tag. I tagged the image ID as "
    "yatinkorat/hellodocker:1.0 (version tag) and also as yatinkorat/hellodocker:latest (used by the Kubernetes "
    "deployment). All three names point to the same image ID."
)
commands(
    "docker tag 9837e200811d yatinkorat/hellodocker:1.0",
    "docker tag 9837e200811d yatinkorat/hellodocker:latest",
    'docker images --filter "reference=hellodocker" --filter "reference=yatinkorat/hellodocker"',
)
shot("03-docker-tag.png", "Figure 3 – image tagged with my Docker Hub username")

doc.add_heading("4. Push the image to Docker Hub", level=2)
para(
    "I pushed the 1.0 tag first. All the layers were uploaded (one base layer was mounted from library/redis "
    "because Docker Hub already had it). Then I pushed latest. Its layers already existed, so only the tag was "
    "added. Both tags have the same digest."
)
commands("docker push yatinkorat/hellodocker:1.0")
shot("04-docker-push-1.0.png", "Figure 4 – docker push yatinkorat/hellodocker:1.0")
commands("docker push yatinkorat/hellodocker:latest")
shot("05-docker-push-latest.png", "Figure 5 – docker push yatinkorat/hellodocker:latest")

doc.add_heading("5. Repository on Docker Hub", level=2)
para(
    "The repository yatinkorat/hellodocker is now public on Docker Hub with both tags (latest and 1.0), "
    "pushed by yatinkorat."
)
shot("15-dockerhub-repo.png", "Figure 6 – yatinkorat/hellodocker repository on Docker Hub (Tags tab)")

# ---------------- PART II ----------------
doc.add_page_break()
doc.add_heading("PART II – Deploying yatinkorat/hellodocker:latest with a Kubernetes Deployment and Service", level=1)

doc.add_heading("6. Update the Kubernetes files to use my own image", level=2)
para(
    "I used the three files from the class repository (pritamworld/DevOps_Kubernetes_exercise10, k8s folder) and "
    "changed the deployment to use my own image instead of the instructor's image:"
)
for b in (
    "hellodocker-deploy.yaml – Deployment with 3 replicas, image yatinkorat/hellodocker:latest, "
    "imagePullPolicy: Always (so Kubernetes pulls it from Docker Hub), NAME env variable, readiness/liveness "
    "probes on port 80 and CPU/memory limits.",
    "hellodocker-service.yaml – NodePort Service hellodocker-nodeport, port 80 → targetPort 80, nodePort 30080.",
    "redis-deploy-service.yaml – Redis Deployment and ClusterIP Service named redis on port 6379 (the app "
    "connects to host \"redis\" to count visits).",
):
    doc.add_paragraph(b, style="List Bullet")
commands("Get-Content hellodocker-deploy.yaml")
shot("06-k8s-files.png", "Figure 7 – hellodocker-deploy.yaml using my image yatinkorat/hellodocker:latest")

doc.add_heading("7. Apply the files", level=2)
para("The kubectl context is minikube. Applying the three files created the two deployments and two services.")
commands(
    "kubectl apply -f hellodocker-deploy.yaml",
    "kubectl apply -f hellodocker-service.yaml",
    "kubectl apply -f redis-deploy-service.yaml",
)
shot("07-kubectl-apply.png", "Figure 8 – kubectl apply")

doc.add_heading("8. Check the rollout", level=2)
para("The rollout waited until all 3 hellodocker replicas were available. Redis also rolled out.")
commands("kubectl rollout status deployment/hellodocker")
shot("08-rollout-status.png", "Figure 9 – deployment \"hellodocker\" successfully rolled out")

doc.add_heading("9. Verify the pods", level=2)
para(
    "All 3 hellodocker pods are Running and Ready (1/1), each with its own IP on the minikube node. "
    "The last command shows every pod runs docker.io/yatinkorat/hellodocker with the same digest that I pushed."
)
commands(
    "kubectl get pods -l app=hellodocker -o wide",
    "kubectl get deployments",
    'kubectl get pods -l app=hellodocker -o custom-columns="POD:.metadata.name,IMAGE:.spec.containers[0].image,'
    'IMAGE_ID:.status.containerStatuses[0].imageID"',
)
shot("09-get-pods.png", "Figure 10 – hellodocker pods running from my Docker Hub image")
para("The pod events confirm Kubernetes pulled the image from Docker Hub.")
commands("kubectl get events --field-selector involvedObject.name=<pod-name> --sort-by=.lastTimestamp")
shot("11-pull-events.png", "Figure 11 – Pulling / Successfully pulled image \"yatinkorat/hellodocker:latest\"")

doc.add_heading("10. Verify the service", level=2)
para(
    "hellodocker-nodeport is a NodePort service that maps port 80 to node port 30080. Its endpoints are the "
    "3 pod IPs. The redis service is a ClusterIP service on port 6379."
)
commands("kubectl get svc hellodocker-nodeport", "kubectl get svc")
shot("10-get-svc.png", "Figure 12 – hellodocker-nodeport service and its endpoints")

doc.add_heading("11. Access the app from Minikube", level=2)
para(
    "minikube service --url printed a local URL and kept a tunnel open, because I'm using the Docker driver on "
    "Windows. I sent several requests with curl. Responses came from different pods (the Hostname changes), "
    "which shows the service load-balancing across the replicas. The Visits counter keeps increasing because it "
    "is stored in Redis. It goes up by more than one between my requests because the readiness and liveness "
    "probes also call \"/\"."
)
commands("minikube service hellodocker-nodeport --url", "curl.exe -s http://127.0.0.1:63065")
shot("12-minikube-service-url.png", "Figure 13 – minikube service URL and curl responses from different pods")
shot("14-browser-app.png", "Figure 14 – the app opened in the browser through the minikube service URL")
para(
    "I also tried the NodePort directly with the minikube IP. From Windows the node IP 192.168.49.2 is not "
    "reachable with the Docker driver, so curl timed out (exit code 28). Running the same curl inside the minikube "
    "node with minikube ssh reaches http://192.168.49.2:30080 and returns the page from different pods."
)
commands(
    "$MINIKUBE_IP = $(minikube ip)",
    "curl.exe -s -m 5 http://${MINIKUBE_IP}:30080",
    'minikube ssh "curl -s http://${MINIKUBE_IP}:30080"',
)
shot("13-nodeport-direct.png", "Figure 15 – NodePort 30080 accessed through the minikube IP")

doc.add_heading("12. Cleanup", level=2)
para(
    "Finally I deleted the deployments and services. After the pods finished terminating, only the default "
    "kubernetes service is left."
)
commands(
    "kubectl delete -f hellodocker-deploy.yaml",
    "kubectl delete -f hellodocker-service.yaml",
    "kubectl delete -f redis-deploy-service.yaml",
)
shot("16-cleanup.png", "Figure 16 – resources deleted")

doc.add_heading("Conclusion", level=1)
para(
    "I published my own image to Docker Hub as yatinkorat/hellodocker (tags 1.0 and latest) and deployed it on "
    "Minikube. Kubernetes pulled the image from Docker Hub, ran 3 replicas behind a NodePort service, and used "
    "Redis as a second service for the visit counter. This shows the step up from a single container to services: "
    "the same image can run anywhere it can be pulled from the registry, and the number of replicas is just a "
    "setting in the deployment file."
)

doc.save(OUT)
print("saved", OUT)
