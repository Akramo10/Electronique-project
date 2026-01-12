# Solution pour l'erreur pandas/numpy

## Problème
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility
```

## Solution sur Ubuntu

Exécutez ces commandes dans l'ordre :

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Désinstaller complètement numpy et pandas
pip uninstall -y numpy pandas

# 3. Installer numpy 2.0.2 d'abord
pip install numpy==2.0.2

# 4. Installer pandas 2.2.2 (compatible avec numpy 2.0.2)
pip install pandas==2.2.2

# 5. Vérifier les versions
pip list | grep -E "numpy|pandas"
```

Vous devriez voir :
- numpy==2.0.2
- pandas==2.2.2

## Alternative : Réinstallation complète

Si le problème persiste, réinstallez toutes les dépendances :

```bash
source venv/bin/activate
pip install --upgrade --force-reinstall -r requirements.txt
```

## Vérification

Testez l'import :

```bash
python3 -c "import pandas as pd; import numpy as np; print('OK: numpy', np.__version__, 'pandas', pd.__version__)"
```

Si cela fonctionne, lancez l'application :

```bash
python3 app1.py
```

