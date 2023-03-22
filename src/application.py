from astask import AsTask

from src import Index, About, Redirect

app = AsTask()
app.route("/", Index)
app.route("/about", About)
app.route("/redirect", Redirect)

if __name__ == "__main__":
    app.run(level="method")
