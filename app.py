from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from os

load_dotenv()
def create_app():
    app = Flask(__name__,template_folder='templates')
    client = MongoClient(os.getenv("MONGODB_URI"))
    app.db = client.my_database

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            city = request.form.get("city")
            phone = request.form.get("phone")
            post = request.form.get("post")

            # Добавляем в базу данных
            project = {
                "first_name": first_name,
                "last_name": last_name,
                "city": city,
                "phone": phone,
                "post": post,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Добавляем время создания
            }

            result = app.db.projects.insert_one(project)
            project_id = result.inserted_id

            print("Entry added:", first_name, last_name, city, phone, post)
            return redirect(url_for('edit_project', project_id=project_id))
        
        projects = app.db.projects.find()  # Получение всех проектов
        return render_template("index2.html", projects=projects)



    @app.route("/edit_project/<string:project_id>", methods=["GET"])
    def edit_project(project_id):
        try:
            project_id = ObjectId(project_id)  # Преобразовываем project_id в ObjectId
        except Exception as e:
            # Обработка ошибки, если project_id неверного формата
            return "Invalid project_id", 400

        project = app.db.projects.find_one({"_id": project_id})

        if project is None:
            # Возвращаем сообщение об ошибке, если проект не найден
            return "Project not found", 404

        return render_template("edit_project.html", project=project, project_id=project_id)



    @app.route("/edit_project/<project_id>/add_step", methods=["POST"])
    def add_step(project_id):
        try:
            project_id = ObjectId(project_id)  # Преобразовываем project_id в ObjectId
        except Exception as e:
            # Обработка ошибки, если project_id неверного формата
            return "Invalid project_id", 400

        step_description = request.form.get("step_description")
        section = request.form.get("section")  # Получаем значение раздела из формы

        # Определите, в какой раздел добавить шаг
        section_field = f"{section}_steps"

        try:
            result = app.db.projects.update_one(
                {"_id": project_id},
                {"$push": {section_field: step_description}}
            )
            if result.modified_count == 0:
                # Если ни одна запись не была изменена, возможно, нет проекта с таким project_id
                return "Project not found", 404
        except Exception as e:
            # Обработка других ошибок, например, проблем с базой данных
            print("Error:", e)
            return "An error occurred", 500

        return redirect(url_for("edit_project", project_id=project_id, current_section=section))


    @app.route("/edit_project/<project_id>/delete_step", methods=["POST"])
    def delete_step(project_id):
        try:
            project_id = ObjectId(project_id)
        except Exception as e:
            return "Invalid project_id", 400

        step_to_delete = request.form.get("step_to_delete")
        section = request.form.get("section")
        
        try:
            result = app.db.projects.update_one(
                {"_id": project_id},
                {"$pull": {f"{section}_steps": step_to_delete}}
            )
            if result.modified_count == 0:
                return "Project not found", 404
        except Exception as e:
            print("Error:", e)
            return "An error occurred", 500

        return redirect(url_for("edit_project", project_id=project_id))



    if __name__ == "__main__":
        app.run(debug=True)
