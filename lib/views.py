from aiohttp.web import Response
from aiohttp.web import View
from aiohttp_jinja2 import render_template

from lib.image import image_to_img_src
from lib.image import PolygonDrawer
from lib.image import open_image

class IndexView(View):
    async def get(self) -> Response:
        return render_template("index.html", self.request, {})

    async def post(self) -> Response:
        try:
            form = await self.request.post()
            file_type = form['image'].filename.split(".")[-1]
            image = open_image(form["image"].file)
            if file_type == "png":
                image = image.convert('RGB')
                image.save('converted_image.jpg')
                image = open_image('converted_image.jpg')
            draw = PolygonDrawer(image)
            model = self.request.app["model"]
            words = []
            for coords, word, accuracy in model.readtext(image):
                draw.highlight_word(coords, word)
                cropped_img = draw.crop(coords)
                cropped_img_b64 = image_to_img_src(cropped_img)
                words.append(
                    {
                        "image": cropped_img_b64,
                        "word": word,
                        "accuracy": accuracy,
                    }
                )
            image_b64 = image_to_img_src(draw.get_highlighted_image())
            ctx = {"image": image_b64, "words": words}
            return render_template("index.html", self.request, ctx)
        except Exception as err:
            ctx = {"error": repr(err)}
            return render_template("index.html", self.request, ctx)
