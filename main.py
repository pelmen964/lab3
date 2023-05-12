import fastapi.responses
import requests
import numpy
import io
import matplotlib.pyplot as plt
from PIL import Image
from googleapiclient.errors import HttpError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Form, File, UploadFile, HTTPException
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import hashlib

app = FastAPI()


# @app.post("/image_form")
# async def make_image(request: Request,
#                     g_recaptcha_response: str = Body(...),
#                      name_op: str = Form(),
#
#                      files: List[UploadFile] = File(description="Multiple files as UploadFile"),

# @app.post("/image_form")
# async def make_image(request: Request,recaptcha_response: str, name_op: str = Form(),files: list = Form()):

# @app.post("/image_form")
# async def make_image(request: Request, name_op: str = Form(...),files: list = Form(...), captcha: str = Form()):

@app.post("/image_form")
async def make_image(request: Request, name_op: str = Form(...),files: list = Form(...), capt: str = Form(...)):

    print(files,name_op,capt)
    recaptcha_response = capt
    try:
        if not recaptcha_response:
            return HTMLResponse("<h1>reCAPTCHA verification failed</h1>")
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": "6LepMsQlAAAAAF13iHkVVQf9fJHTrhZ7nbOmd3a7",
                "response": recaptcha_response,
            },
        )
        if not response.json().get("success"):
            return HTMLResponse("<h1>reCAPTCHA verification failed</h1>")

        ready = False
        print(len(files))
        if (len(files) > 0):
            if (len(files[0].filename) > 0):
                ready = True
        images = []
        if ready:
            # print([file.filename.encode('utf-8') for file in files])
            # преобразуем именя файлов в хэш строку
            images = ["static/" + hashlib.sha256(file.filename.encode('utf8')).hexdigest() for file in files]

            last_name = "static/" + hashlib.sha256(
                files[0].filename.encode('utf8') + files[1].filename.encode('utf8')).hexdigest()

            content = [await file.read() for file in files]
            # создаем объекты Image типа RGB размером 200 на 200

            p_images = [Image.open(io.BytesIO(con)).convert("RGB").resize((400, 400)) for con in
                        content]

            img = numpy.array(p_images[0])
            r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            plt.hist(r.flatten(), bins=256, color='red', alpha=0.5)
            plt.hist(g.flatten(), bins=256, color='green', alpha=0.5)
            plt.hist(b.flatten(), bins=256, color='blue', alpha=0.5)
            # plt.show()
            plt.savefig('static/plot1.png')

            img = numpy.array(p_images[1])
            r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            plt.hist(r.flatten(), bins=256, color='red', alpha=0.5)
            plt.hist(g.flatten(), bins=256, color='green', alpha=0.5)
            plt.hist(b.flatten(), bins=256, color='blue', alpha=0.5)
            # plt.show()
            plt.savefig('static/plot2.png')

            if name_op == 'horizontal':
                img = Image.new("RGB", (800, 400))
                img = numpy.array(img)

                img1 = numpy.array(p_images[0])
                img2 = numpy.array(p_images[1])

                img[0:400, 0:400, :] = img1[0:400, 0:400, :]
                img[0:400, 400:800, :] = img2[0:400, 0:400, :]
                # p_images[i]
            else:
                img = Image.new("RGB", (400, 800))
                img = numpy.array(img)

                img1 = numpy.array(p_images[0])
                img2 = numpy.array(p_images[1])

                img[0:400, 0:400] = img1[0:400, 0:400]
                img[400:800, 0:400] = img2[0:400, 0:400]

            r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            plt.hist(r.flatten(), bins=256, color='red', alpha=0.5)
            plt.hist(g.flatten(), bins=256, color='green', alpha=0.5)
            plt.hist(b.flatten(), bins=256, color='blue', alpha=0.5)
            # plt.show()
            plt.savefig('static/plot3.png')

            img = Image.fromarray(img)
            plt.imshow(img)
            plt.show()
            img.save("./" + last_name + ".jpeg", 'JPEG')
            rets = [f"{last_name}.jpeg", 'static/plot1.png', 'static/plot2.png', 'static/plot3.png']
            # возвращаем html с параметрами ссылками на изображения, которые потом  будут
            # извлечены браузером запросами get по указанным ссылкам в img  src
            return templates.TemplateResponse("forms.html", {"request": request, "ready": ready, "images": rets})

    except HttpError as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/image_form", response_class=HTMLResponse)
async def make_image(request: Request):
    return templates.TemplateResponse("forms.html", {"request": request})



def sum_two_args(x, y):
    return x + y

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Hello World route

# Декоратор определяющий маршрут для Get запроса
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# возвращаем some.html сгенерированный из шаблона
# передав туда одно значение something
@app.get("/some_url/{something}", response_class=HTMLResponse)
async def read_something(request: Request, something: str):
    return templates.TemplateResponse("start_page.html", {"request": request, "something": something})


def create_some_image(some_difs):
    imx = 200
    imy = 200
    image = numpy.zeros((imx, imy, 3), dtype=numpy.int8)
    image[0:imy // 2, 0:imx // 2, 0] = some_difs
    image[imy // 2:, imx // 2:, 2] = 240
    image[imy // 2:, 0:imx // 2, 1] = 240
    return image


# возврат изображения в виде потока медиа данных по URL
@app.get("/bimage", response_class=fastapi.responses.StreamingResponse)
async def b_image(request: Request):
    image = create_some_image(100)
    im = Image.fromarray(image, mode="RGB")
    # сохраняем изображение в буфере оперативной памяти
    imgio = io.BytesIO()
    im.save(imgio, 'JPEG')
    imgio.seek(0)
    # Возвращаем изображение в виде mime типа image/jpeg
    return fastapi.responses.StreamingResponse(content=imgio,
                                               media_type="image/jpeg")


# возврат двух изображений в таблице html, одна ячейка ссылается на url bimage
# другая ячейка указывает файл из папки static по ссылке
# при этом файл туда предварительно сохраняется после генерации из массива
@app.get("/image", response_class=HTMLResponse)
async def make_image(request: Request):
    image_n = "image.jpg"
    image_dyn = request.base_url.path + "bimage"
    image_st = request.url_for("static", path=f'/{image_n}')
    image = create_some_image(250)
    im = Image.fromarray(image, mode="RGB")
    im.save(f"./static/{image_n}")
    # передаем в шаблон две переменные к которых сохранили url-ы
    return templates.TemplateResponse("image.html", {"request": request,
                                                     "im_st": image_st, "im_dyn": image_dyn})
