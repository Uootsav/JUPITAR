# Windows installation

End users: read END_USER_INSTALL.md. You need a successfully built installer,
not Python, Ollama or the source scripts.

Publisher: read GET_INSTALLER.md to generate the installer on GitHub. The source
ZIP does not contain a compiled EXE. The Windows workflow has not been run here.

Developer-only build: tools/build_windows.ps1. It requires Python 3.11, Git,
CMake, Visual Studio C++ build tools and Inno Setup 6 on the build machine only.
Do not ask consumers to run this build script.

For the 0.4 visual/progress/website update, follow UPDATE_AND_PUBLISH.md.
