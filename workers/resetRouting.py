import os
from PyQt5.QtCore import QObject, pyqtSignal, QProcess
from utils import read, write, generate, tab
import paths

class ResetRoutingWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    success = pyqtSignal(bool)

    def __init__(self, path : str, options : dict) -> None:
        super().__init__()
        self.path = path
        self.options = options

    def update_routes(self):
        # Routes
        if os.path.exists(paths.TEMPLATES + "routes/web.txt"):
            web_path = self.path + paths.ROUTES + "web.php"
            admin_middleware_routes = []
            for modeltitle, value in self.options["models"].items():
                if modeltitle == "Admin":
                    continue
                
                d = {
                    "{model_title_lower}" : str.lower(modeltitle),
                    "{model_title}" : modeltitle,
                    "{model_name_slug}" : value["model_slug"],
                }
                admin_middleware_routes.append(generate(read(paths.SNIPPETS + "routes/normal-routes.txt"), d))

                if value["multiple_image"]:
                    admin_middleware_routes.append(generate(read(paths.SNIPPETS + "routes/multiple-image-routes.txt"), d))

                if value["sorting"]:
                    admin_middleware_routes.append(generate(read(paths.SNIPPETS + "routes/sorting-route.txt"), d))

                if value["single_active"] or value["multiple_active"]:
                    admin_middleware_routes.append(generate(read(paths.SNIPPETS + "routes/activate-route.txt"), d))

                for field in value["fields"]:
                    if field["type"] == "boolean" and field["show"]:
                        admin_middleware_routes.append(generate(read(paths.SNIPPETS + "routes/boolean-route.txt"), {
                            "{model_title_lower}" : str.lower(modeltitle),
                            "{model_title}" : modeltitle,
                            "{model_name_slug}" : value["model_slug"],
                            "{field_slug}" : field["field_slug"],
                            "{field_title}" : str.title(field["field_name"]).replace(" ", "")
                        }))

            if os.path.exists(web_path):
                d = {
                    "{use_controllers}" : "".join(["use App\\Http\\Controllers\\" + modeltitle + "Controller;\n" for modeltitle, values in self.options["models"].items() if values.get("use_controller") == True]),
                    "{pages}" : "",
                    "{admin}" : generate(read(paths.SNIPPETS + "admin/admin-routes.txt"), {"{admin_middleware_routes}": tab("\n".join(admin_middleware_routes))})
                }

                generated_text = generate(read(paths.TEMPLATES + "routes/web.txt"), d)
                write(generated_text, web_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + web_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "routes/web.txt")
            self.process_finished(False)

        # Update admin layout
        self.log.emit("Updating admin layout...")
        admin_layout_path = paths.TEMPLATES + "views/admin/admin-layout.txt"
        if os.path.exists(admin_layout_path):
            if not os.path.isdir(self.path + paths.VIEWS + "admin"):
                os.mkdir(self.path + paths.VIEWS + "admin")

            layout_path = self.path + paths.VIEWS + "admin/layout.blade.php"
            li_path = paths.SNIPPETS + "admin/admin-layout-li.txt"
            li_items = []
            if os.path.exists(li_path):
                for modeltitle, value in self.options["models"].items():
                    if modeltitle == "Admin":
                        continue
                    
                    data = {
                        "{model_name_slug}" : value["model_slug"],
                        "{model_title}" : value["model_title"],
                        "{model_name}" : value["model_name"],
                    }

                    li_items.append(generate(read(li_path), data))
                write(generate(read(admin_layout_path), {"{layout_list_items}" : tab("\n".join(li_items), 3)}), layout_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + li_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + admin_layout_path)
            self.process_finished(False)

        self.process_finished(True)

    def process_finished(self, success = True):
        self.success.emit(success)
        self.finished.emit()