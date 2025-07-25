# Inpainting
InPainting Recreation Project 

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

2.a. make noteboook kernel:
```bash
conda install -c anaconda ipykernel -y
python -m ipykernel install --user --name inpaint --display-name "inpaint"
``` 

3. Install the required packages:
```bash
pip install -r requirements.txt
```

### Run Server (Backend)
open a terminal and run the following command:
```bash
conda activate inpaint
cd src/backend
uvicorn main:app --reload
```

### Run Webapp (Frontend)
```bash
conda activate inpaint
cd src/frontend
streamlit run app.py
```


### Contributors :
* Yalla Mahanth 
* Md Kaif Alam 