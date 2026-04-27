# DharmaPath Kundli Web App

FastAPI + Swiss Ephemeris + GeoNames location lookup.

## Install on Debian/GCP

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip

unzip dharmapath_kundli_webapp.zip
cd dharmapath_kundli_webapp

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Set GeoNames username

Create free GeoNames account and enable free web services. Then:

```bash
export GEONAMES_USERNAME="your_geonames_username"
```

If you skip this, the app uses `demo`, which may be limited.

## Run locally on VM

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open in browser:

```text
http://YOUR_VM_EXTERNAL_IP:8000
```

Make sure GCP firewall allows TCP port 8000.

## Best accuracy

Put Swiss Ephemeris `.se1` files inside:

```text
ephe/
```

The app uses local Swiss Ephemeris for astrology calculations. It does not call an astrology API.
