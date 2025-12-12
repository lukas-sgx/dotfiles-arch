# Jenkins on Ubuntu 24.04 (Docker)

Image minimale qui installe Jenkins (paquet officiel) sur `ubuntu:24.04`.

### Caractéristiques
- Base : `ubuntu:24.04`
- Java : OpenJDK 17
- Ports exposés : 8080 (HTTP), 50000 (agent)
- Volume recommandé : `/var/lib/jenkins` (JENKINS_HOME)

### Build

```sh
# depuis le dossier contenant le Dockerfile
docker build -t my-jenkins:ubuntu24.04 .
```

### Lancement

```sh
# lance Jenkins et persiste les données dans un volume nommé 'jenkins_home'
docker run -d \
  --name my-jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/lib/jenkins \
  my-jenkins:ubuntu24.04
```

### Mot de passe initial
Après le premier démarrage, le mot de passe administrateur initial se trouve dans le container:

```sh
docker exec -it my-jenkins cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Notes
- Le Dockerfile utilise le paquet officiel Jenkins (dépôt pkg.jenkins.io). Le conteneur démarre Jenkins en exécutant directement le fichier `jenkins.war` installé par le paquet. Cela évite d'avoir à exécuter systemd dans le conteneur.
- Si vous préférez la configuration officielle et optimisée par Jenkins, consultez l'image officielle `jenkins/jenkins` sur Docker Hub.

