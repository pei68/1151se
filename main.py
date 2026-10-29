# main.py
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB,lifespan

#from routes import router as all_routes
#from routes.upload import router as upload_router
#from routes import users


templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)

# Include the router
# app.include_router("routes/r", prefix="/") #mount every thing from ./routes/ to url under prefix#

@app.get("/students/list")
async def read_users(db=Depends(getDB)):
	cur=await db.execute("SELECT * FROM students")
	return await cur.fetchall()

@app.get("/students/list/template")
async def stuList(request:Request, db=Depends(getDB)):
	cur=await db.execute("SELECT * FROM students order by stuid;")
	data= await cur.fetchall()
	return templates.TemplateResponse(name="studentList.html", request=request,context={"students": data})

@app.get("/student/edit/{stuid}")
async def stuEdit(stuid:int,request:Request, db=Depends(getDB)):
	cur=await db.execute("SELECT * FROM students where stuid=%s",(stuid,))
	data= await cur.fetchone()
	return templates.TemplateResponse(name="studentEdit.html", request=request,context={"data": data})


@app.post("/student/update")
async def stuUpdate(stuid:int=Form(...), name:str=Form(...), height:int=Form(...), db=Depends(getDB)):
	print(stuid, name, height)
	await db.execute("update students set name=%s, height=%s where stuid=%s;", (name, height, stuid))
	return RedirectResponse(url="/students/list/template",status_code=303) #use 303 to switch to GET

@app.get("/student/delete/{stuid}")
async def stuDelete(stuid: int, db = Depends(getDB)):
    # 執行 SQL 刪除該學號的學生
    await db.execute("DELETE FROM students WHERE stuid = %s;", (stuid,))
    # 刪除完成後，重新導向回學生清單頁面
    return RedirectResponse(url="/students/list/template", status_code=303)

# 1. 顯示新增學生的表單頁面
@app.get("/student/add")
async def stuAddPage(request: Request):
    return templates.TemplateResponse(name="studentAdd.html", request=request)

# 2. 接收表單送出的資料並存入資料庫
@app.post("/student/create")
async def stuCreate(stuid: int = Form(...), name: str = Form(...), height: int = Form(...), db = Depends(getDB)):
    # 執行 SQL 插入新資料（可根據你資料庫實際欄位調整，此處以 stuid, name, height 為例）
    await db.execute("INSERT INTO students (stuid, name, height) VALUES (%s, %s, %s);", (stuid, name, height))
    # 新增完成後，重新導向回學生清單頁面
    return RedirectResponse(url="/students/list/template", status_code=303)