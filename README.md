# Inpainting

This project provides a web application for inpainting images, allowing users to upload images, auto detect the objects and prompts user to select areas to inpaint, and view the results.


![Inpainting](assets/inpaint.jpg)

    
---


## Setup 

1. Clone the repository:
```bash
git clone https://github.com/Mahanth-Maha/Inpainting.git
cd Inpainting
```

2. Create a virtual environment:
```bash 
conda create -n inpaint python=3.9 -y 
conda activate inpaint

```

2. install ipykernel to work in jupyter notebook:
```bash
conda install -c anaconda ipykernel -y
python -m ipykernel install --user --name inpaint --display-name "inpaint"

``` 

3. Install pytorch package by visit [pytorch.org](https://pytorch.org/get-started/locally/) 

   or use the following command for CUDA 12.8:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

```

4. Install the required packages:
```bash
pip install -r requirements.txt

```

5. create `.env` file by copying `env_template`:
```bash
cp env_template .env

```
 - fill the `.env` file with the required environment variables. 
    - You can use the following values for testing:
```python
# .env default settings
ANNOTE_MAPPING_FILE_PATH="models/annotations/coco_category_mapping.json"
DEBUG_LEVEL="INFO"
```


### Run Server (Backend)
open a terminal and run the following command (keep this terminal open):
```bash
conda activate inpaint
cd src/backend
uvicorn main:app --reload

```

### Run Webapp (Frontend)
Open another terminal and run the following command (keep this terminal open):
```bash
conda activate inpaint
cd src/frontend
streamlit run app.py

```
It will launch the web app in your default browser, usually at [http://localhost:8501](http://localhost:8501).

## Contributors :
* Yalla Mahanth -  mahanthyalla [at] iisc.ac.in
* Md Kaif Alam  - kaifalam [at] iisc.ac.in