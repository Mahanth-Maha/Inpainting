# DEVELOPMENT Commands




### Canvas Mask Component - Build Instructions
```bash
conda activate inpaint
cd src/frontend/components/canvas_mask/
npm install
npm run build

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

