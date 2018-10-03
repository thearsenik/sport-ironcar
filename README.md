# Ironcar
Mini-car, big challenge!

## Le simulateur

### Pré-requis
- Installer Blender 3D v.2.79b
- Installer Anaconda (et donc Spyder)

### Utilisation
1. Ouvrir ./blender/road.blend avec Blender 3D
2. Ouvrir l'éditeur de scripts (Window > Scripting) et charger le fichier ./simulateur/blenderController.py
3. Ouvrir ./simulateur/imageAnalyser.py avec Spyder
4. Lancer le code python dans Spyder
5. Lancer le code python dans Blender

&rarr; Il existe une variable *NB_ITERATIONS* dans *imageAnalyser.py* qui définit quand la simulation s'arrête (1 itération = 1 image, à raison de 24 images / secondes).

&rarr; A la fin de la simulation, le répertoire défini par la variable *imageDebugDir* du code de *imageAnalyser.py* contient toutes les images et le répertoire *videoOuputFile* contient la vidéo assemblée à partir de toutes ces images.

&rarr; Blender 3D ne s'arrêtant pas tout seul, une solution est de mettre le texte `stop` dans le fichier pointé par la variable *jsonOutputFile*
