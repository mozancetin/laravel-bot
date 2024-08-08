import os
from PyQt5.QtCore import QObject, pyqtSignal, QProcess
from utils import read, write, generate, tab
import paths

class CreateModelWorker(QObject):

    log = pyqtSignal(str)
    finished = pyqtSignal()
    success = pyqtSignal(bool)

    def __init__(self, path : str, options : dict):
        super().__init__()
        self.path = path
        self.options = options

    def start(self):
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(lambda: self.logger("output"))
        self.process.readyReadStandardError.connect(lambda: self.logger("error"))
        self.process.finished.connect(self.generate_files)

        self.process.start('cmd')
        self.process.waitForStarted()
        self.log.emit("Process has been started...")
        self.process.write((f"cd {self.path}\n").encode())
        self.process.write((f"php artisan make:model {self.options['model_title']}\n").encode())
        self.process.write((f"php artisan make:controller {self.options['model_title']}Controller\n").encode())
        if self.options["multiple_image"]:
            self.process.write((f"php artisan make:model {self.options['model_title']}Image\n").encode())

        self.process.write(('exit\n').encode())

    def check_paths(self, path1 : str, path2 : str = None):
        if os.path.exists(paths.TEMPLATES + path1):
            if path2 != None:
                if not os.path.exists(path2):
                    self.log.emit("Belirtilen yol bulunamadı: " + path2)
                    self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + path1)
            self.process_finished(False)

    def generate_files(self):
        general_migration_path = "migrations/GeneralMigration.txt"
        self.check_paths(general_migration_path)
        migration_file_path = self.path + paths.MIGRATION + f"3000_create_{self.options['model_slug']}_migration.php"

        if self.options["multiple_image"]:
            image_class_migration_path = self.path + paths.MIGRATION + f"3001_create_{self.options['model_slug']}_image_migration.php"
            image_class_model_path = self.path + paths.MODELS + f"{self.options['model_title']}Image.php"

        general_model_path = "models/GeneralModel.txt"
        model_path = self.path + paths.MODELS + f"{self.options['model_title']}.php"
        self.check_paths(general_model_path, model_path)

        if self.options["use_controller"]:
            if not self.options["multiple_image"]:
                general_controller_path = "controllers/GeneralController.txt"
            else:
                general_controller_path = "controllers/GeneralControllerWithMultipleImage.txt"

            controller_path = self.path + paths.CONTROLLERS + f"{self.options['model_title']}Controller.php"
            self.check_paths(general_controller_path, controller_path)

        model_list_path = "views/model-list.txt"
        self.check_paths(model_list_path)

        model_create_path = "views/model-create.txt"
        self.check_paths(model_create_path)

        if self.options["multiple_image"]:
            model_image_list_path = "views/model-image-list.txt"
            self.check_paths(model_image_list_path)

        if not os.path.isdir(self.path + paths.IMAGES + self.options["model_slug"]):
            os.mkdir(self.path + paths.IMAGES + self.options["model_slug"])

        if not os.path.isdir(self.path + paths.IMAGES + self.options["model_slug"] + "/resized"):
            os.mkdir(self.path + paths.IMAGES + self.options["model_slug"] + "/resized")

        slug_field = ""
        field_names = []
        for field in self.options["fields"]:
            field_names.append("'" + field['field_slug'] + "'")
            if field["slug"]:
                slug_field = field["field_slug"]
                field_names.append("'slug'")

        # Migration -------------------------------------------------------------------------------------------------------------------------------------------
        self.log.emit("Creating the migration file...")
        write("", migration_file_path)
        self.log.emit(f"Generating the {self.options['model_title']} migration...")
        
        d = dict()
        d["{model_name_slug}"] = self.options['model_slug']
        migration_lines = []
        for field in self.options['fields']:
            attr = "->".join([k + "()" for k, v in field.items() if v == True and k not in ["slug", "show"]]) if field["type"] != "boolean" else f"default({'true' if field['default'] else 'false'})"
            migration_lines.append(generate(read(paths.SNIPPETS + "migration_line.txt"), {
                "{field_type}" : field['type'],
                "{field_name}" : field['field_slug'],
                "{attr}" : "->" + attr if attr != "" else attr
            }))

        if self.options["single_active"] or self.options["multiple_active"]:
            migration_lines.append("$table->boolean('active')->default(true);")

        if self.options["sorting"]:
            migration_lines.append("$table->integer('sort_order')->unsigned()->nullable();")

        if self.options["image"]:
            migration_lines.append("$table->string('image_path')" + ("->nullable();" if not self.options["image_required"] else ";"))

        if slug_field != "":
            migration_lines.append("$table->string('slug');")

        d["{model_migration}"] = tab("\n".join(migration_lines) + "\n", 3)
        generated_migration = generate(read(paths.TEMPLATES + "migrations/GeneralMigration.txt"), d)
        
        write(generated_migration, migration_file_path)
        self.log.emit("Migration generated")

        if self.options["multiple_image"]:
            self.log.emit("Generating model image class migration")
            write("", image_class_migration_path)

            d = dict()
            d["{model_name_slug}"] = self.options['model_slug'] + "_image"
            migration_lines = [f"$table->foreignId('{self.options['model_slug']}_id')->constrained();", "$table->string('image_path');", "$table->integer('sort_order')->unsigned()->nullable();"]
            d["{model_migration}"] = tab("\n".join(migration_lines) + "\n", 3)
            generated_image_migration = generate(read(paths.TEMPLATES + "migrations/GeneralMigration.txt"), d)
            write(generated_image_migration, image_class_migration_path)
            self.log.emit("Model image class migration generated")


        # Model -------------------------------------------------------------------------------------------------------------------------------------------
        self.log.emit(f"Generating the {self.options['model_title']} model...")
        
        addons = []
        if self.options["single_active"] or self.options["multiple_active"]:
            addons.append("'active'")

        if self.options["sorting"]:
            addons.append("'sort_order'")

        if self.options["image"]:
            addons.append("'image_path'")

        d = {
            "{model_title}" : self.options['model_title'],
            "{model_name_slug}" : self.options['model_slug'],
            "{fillable}" : ", ".join(field_names + addons),
            "{additional_functions}" : tab(generate(read(paths.SNIPPETS + "model_has_many.txt"), {
                "{relation_slug}" : "images", 
                "{relation_class_title}" : self.options['model_title'] + "Image", 
                "{relation_slug_id}" : self.options['model_slug']})) if self.options["multiple_image"] else "",
            "{slug}" : ""
        }
        if slug_field != "":
            d["{slug}"] = generate(read(paths.SNIPPETS + "slug.txt"), {"{model_slug}" : self.options["model_slug"], "{slug_field}" : slug_field})

        generated_text = generate(read(paths.TEMPLATES + "models/GeneralModel.txt"), d)
        
        write(generated_text, model_path)
        self.log.emit("Model generated")

        if self.options["multiple_image"]:
            self.log.emit(f"Generating the {self.options['model_title']}Image model...")
            d = {
                "{model_title}" : self.options['model_title'] + "Image",
                "{model_name_slug}" : self.options['model_slug'] + "_image",
                "{fillable}" : f"'{self.options['model_slug']}_id', 'image_path', 'sort_order'",
                "{additional_functions}" : tab(generate(read(paths.SNIPPETS + "model_belongs_to.txt"), {
                    "{relation_slug}" : self.options['model_slug'], 
                    "{relation_class_title}" : self.options['model_title'],
                    "{relation_slug_id}" : self.options['model_slug'], 
                    })),
                "{slug}" : ""
            }

            generated_text = generate(read(paths.TEMPLATES + "models/GeneralModel.txt"), d)
        
            write(generated_text, image_class_model_path)
            self.log.emit("Model image class generated")

        # Controller -------------------------------------------------------------------------------------------------------------------------------------------
        if self.options["use_controller"]:
            self.log.emit(f"Generating the {self.options['model_title']}Controller...")
            
            additional_imports = []
            additional_store_code = []
            additional_update_code = []
            additional_destroy_code = []
            additional_functions = []

            data = {
                "{model_controller}" : self.options["model_title"] + "Controller",
                "{model_name_slug}" : self.options["model_slug"],
                "{model_title}" : self.options["model_title"],
                "{model_name}" : self.options["model_name"],
                "{order}": "'sort_order'" if self.options["sorting"] else "'created_at', 'desc'",
                "{store_image_code}" : "",
                "{update_image_code}" : "",
                "{destroy_image_code}" : "",
                "{move_function}" : "",
                "{additional_store_code}" : "",
                "{additional_update_code}" : "",
                "{additional_destroy_code}" : "",
                "{additional_functions}" : "",
                "{store_validation}" : "",
                "{update_validation}" : "",
                "{additional_imports}" : "",
            }
            store_val = []
            for field in self.options["fields"]:
                if field["type"] != "boolean":
                    store_val.append(f"'{field['field_slug']}' => '" + ("nullable" if field["nullable"] else "required") + "|" + ("int" if field["type"] == "integer" else "string") + "',")
                else:
                    to_append = generate(read(paths.SNIPPETS + "boolean_validation.txt"), {"{field_name}" : field["field_slug"]})
                    additional_store_code.append(to_append)
                    additional_update_code.append(to_append)
                    additional_functions.append(generate(read(paths.SNIPPETS + "change_bool_function.txt"), {
                        "{field_title}" : str.title(field["field_name"]).replace(" ", ""),
                        "{model_name_slug}" : self.options["model_slug"],
                        "{field_slug}" : field["field_slug"],
                        "{model_title}" : self.options["model_title"],
                    }))

            update_val = [] + store_val

            if self.options["single_active"] or self.options["multiple_active"]:
                to_append = generate(read(paths.SNIPPETS + "boolean_validation.txt"), {"{field_name}" : "active"})
                additional_store_code.append(to_append)
                additional_update_code.append(to_append)
                if self.options["multiple_active"]:
                    additional_functions.append(tab(generate(read(paths.SNIPPETS + "multiple_active_function.txt"), data)))
                else:
                    additional_functions.append(tab(generate(read(paths.SNIPPETS + "single_active_function.txt"), data)))

            if self.options["image"] or self.options["multiple_image"]:
                additional_imports.append("use Intervention\Image\ImageManagerStatic as Image;")
                if self.options["image"]:
                    if self.options["image_required"]:
                        store_val.append("'image_path' => 'required|image|mimes:jpeg,png,jpg,gif',")
                    else:
                        store_val.append("'image_path' => 'nullable|image|mimes:jpeg,png,jpg,gif',")
                    update_val.append("'image_path' => 'nullable|image|mimes:jpeg,png,jpg,gif',")
                    data["{store_image_code}"] = tab(generate(read(paths.SNIPPETS + "image_store.txt"), data), 2)
                    data["{update_image_code}"] = tab(generate(read(paths.SNIPPETS + "image_update.txt"), data), 2)
                    data["{destroy_image_code}"] = tab(generate(read(paths.SNIPPETS + "image_destroy.txt"), data), 2)

            if self.options["sorting"]:
                data["{move_function}"] = tab(generate(read(paths.SNIPPETS + "move_function.txt"), data))
                additional_store_code.append(generate(read(paths.SNIPPETS + "sort_store.txt"), data))
                additional_destroy_code.append(generate(read(paths.SNIPPETS + "sort_destroy.txt"), data))

            if len(additional_store_code) > 0:
                data["{additional_store_code}"] = tab("\n".join(additional_store_code), 2)

            if len(additional_update_code) > 0:
                data["{additional_update_code}"] = tab("\n".join(additional_update_code), 2)

            if len(additional_destroy_code) > 0:
                data["{additional_destroy_code}"] = tab("\n".join(additional_destroy_code), 2)

            if len(additional_functions) > 0:
                data["{additional_functions}"] = tab("\n".join(additional_functions))

            if len(additional_imports) > 0:
                data["{additional_imports}"] = "\n".join(additional_imports)

            data["{store_validation}"] = tab("\n".join(store_val), 3)
            data["{update_validation}"] = tab("\n".join(update_val), 3)
            
            generated_controller = generate(read(paths.TEMPLATES + general_controller_path), data)

            write(generated_controller, controller_path)
            self.log.emit("Controller generated")
        

            # List View -------------------------------------------------------------------------------------------------------------------------------------------
            th_fields = []
            fields = []
            additional_scripts = []
            additional_header = []
            data = {
                "{model_name_slug}" : self.options["model_slug"],
                "{model_title}" : self.options["model_title"],
                "{model_name}" : self.options["model_name"],
                "{sortable}" : "",
            }

            if self.options["sorting"]:
                th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : "Sıralama"}))
                fields.append(generate(read(paths.SNIPPETS + "views/list-td-normal.txt"), {"{field_slug}" : "sort_order", "{model_name_slug}" : data["{model_name_slug}"]}))
                additional_header.append(read(paths.SNIPPETS + "scripts/sorting-h.txt"))
                additional_scripts.append(generate(read(paths.SNIPPETS + "scripts/sorting-s.txt"), {"{model_name_slug}" : data["{model_name_slug}"]}))
                data["{sortable}"] = generate(read(paths.SNIPPETS + "views/list-tr-sortable.txt"), {"{model_name_slug}" : data["{model_name_slug}"]})

            if self.options["multiple_image"]:
                th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : "İmaj"}))
                if self.options["image"]:
                    fields.append(generate(read(paths.SNIPPETS + "views/list-td-image-s.txt"), {"{model_name_slug}" : data["{model_name_slug}"]}))
                else:
                    fields.append(generate(read(paths.SNIPPETS + "views/list-td-image-m.txt"), {"{model_name_slug}" : data["{model_name_slug}"]}))
                
                th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : "Fotoğraflar"}))
                fields.append(generate(read(paths.SNIPPETS + "views/list-td-show-m-image.txt"), {"{model_name_slug}" : data["{model_name_slug}"]}))
                
            else:
                if self.options["image"]:
                    th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : "İmaj"}))
                    fields.append(generate(read(paths.SNIPPETS + "views/list-td-image-s.txt"), {"{model_name_slug}" : data["{model_name_slug}"]}))  

            for field in self.options["fields"]:
                if field["show"] and field["type"] != "text":
                    th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : field["field_name"]})) # 5 tab
                    if field["type"] == "boolean":
                        file = "views/list-td-bool.txt"
                        additional_scripts.append(generate(read(paths.SNIPPETS + "scripts/boolean-s.txt"), {"{model_title_lower}" : str.lower(self.options["model_title"]), "{model_name_slug}" : self.options["model_slug"], "{field_slug}" : field["field_slug"]}))
                    else:
                        file = "views/list-td-normal.txt"

                    fields.append(generate(read(paths.SNIPPETS + file), {"{field_slug}" : field["field_slug"], "{model_name_slug}" : data["{model_name_slug}"]})) # 6 tab

            if self.options["single_active"] or self.options["multiple_active"]:
                th_fields.append(generate(read(paths.SNIPPETS + "views/list-th.txt"), {"{field_name}" : "Aktif"}))
                fields.append(generate(read(paths.SNIPPETS + "views/list-td-bool.txt"), {"{field_slug}" : "active", "{model_name_slug}" : data["{model_name_slug}"]})) # 6 tab
                if self.options["multiple_active"]:
                    additional_scripts.append(generate(read(paths.SNIPPETS + "scripts/boolean-s.txt"), {"{model_title_lower}" : str.lower(self.options["model_title"]), "{model_name_slug}" : self.options["model_slug"], "{field_slug}" : "active"}))
                else:
                    additional_scripts.append(generate(read(paths.SNIPPETS + "scripts/single-active-s.txt"), {"{model_title_lower}" : str.lower(self.options["model_title"]), "{model_name_slug}" : self.options["model_slug"]}))

            data["{additional_header}"] = tab("\n".join(additional_header))
            data["{th_fields}"] = tab("\n".join(th_fields), 5)
            data["{fields}"] = tab("\n".join(fields), 6)
            data["{additional_scripts}"] = "\n".join(additional_scripts)

            generated_model_list = generate(read(paths.TEMPLATES + model_list_path), data)
            write(generated_model_list, self.path + paths.VIEWS + "/admin/" + self.options['model_slug'] + "-list.blade.php")

            # Create View -------------------------------------------------------------------------------------------------------------------------------------------
            items = []
            additional_scripts = []
            additional_header = []
            sweetalert = []
            data = {
                "{model_name_slug}" : self.options["model_slug"],
                "{model_title}" : self.options["model_title"],
                "{model_name}" : self.options["model_name"],
                "{model_title_lower}" : str.lower(self.options["model_title"]),
                "{additional_scripts}" : "",
            }

            field_data = data.copy()
            tiny = False
            for field in self.options["fields"]:
                field_data["{field_slug}"] = field["field_slug"]
                field_data["{field_name}"] = field["field_name"]
                field_data["{type}"] = field["type"]
                field_data["{is_required}"] = "required" if not field["nullable"] else ""
                if field["type"] == "string":
                    temp_path = paths.SNIPPETS + "views/create-str.txt"
                elif field["type"] == "text":
                    temp_path = paths.SNIPPETS + "views/create-text.txt"
                elif field["type"] == "integer":
                    temp_path = paths.SNIPPETS + "views/create-int.txt"
                else: # Boolean
                    temp_path = paths.SNIPPETS + "views/create-bool.txt"

                items.append(generate(read(temp_path), field_data))
                if field["type"] == "boolean":
                    continue

                if not field["nullable"]:
                    if field["type"] != "text":
                        sweetalert.append(generate(read(paths.SNIPPETS + "scripts/sweetalert-item.txt"), field_data))
                    else:
                        if not tiny:
                            additional_scripts.append(read(paths.SNIPPETS + "scripts/tinymce-init.txt"))
                            tiny = True
                        sweetalert.append(generate(read(paths.SNIPPETS + "scripts/sweetalert-tinymce.txt"), field_data))
            
            if self.options["image"]:
                items.append(generate(read(paths.SNIPPETS + "views/create-image.txt"), data))
                if self.options["image_required"]:
                    items.append(generate(read(paths.SNIPPETS + "views/create-image-input.txt"), data))
                    sweetalert.append(generate(read(paths.SNIPPETS + "scripts/sweetalert-image.txt"), data))

            if self.options["multiple_image"]:
                items.append(read(paths.SNIPPETS + "views/create-multi-image-input.txt"))
                items.append(generate(read(paths.SNIPPETS + "views/create-multi-image.txt"), data))
                sweetalert.append(read(paths.SNIPPETS + "scripts/sweetalert-multi-image.txt"))
                additional_header.append(read(paths.SNIPPETS + "scripts/sorting-h.txt"))
                additional_scripts.append(generate(read(paths.SNIPPETS + "scripts/create-multi-image-s.txt"), data))

            if self.options["single_active"] or self.options["multiple_active"]:
                items.append(generate(read(paths.SNIPPETS + "views/create-bool.txt"), {"{model_name_slug}" : self.options["model_slug"], "{field_slug}" : "active", "{field_name}" : "Aktif"}))

            data["{additional_header}"] = tab("\n".join(additional_header))
            additional_scripts.append(generate(read(paths.TEMPLATES + "sweetalert-template.txt"), {"{sweet_items}" : tab("\n\n".join(sweetalert))}))
            data["{additional_scripts}"] = "\n".join(additional_scripts)
            data["{items}"] = tab("\n\n".join(items), 2)

            generated_model_create = generate(read(paths.TEMPLATES + model_create_path), data)
            write(generated_model_create, self.path + paths.VIEWS + "/admin/" + self.options['model_slug'] + "-create.blade.php")

            # Image List View -------------------------------------------------------------------------------------------------------------------------------------------
            if self.options["multiple_image"]:
                data["{model_title_lower}"] = str.lower(data["{model_title}"])
                generated_model_image_list = generate(read(paths.TEMPLATES + model_image_list_path), data)
                write(generated_model_image_list, self.path + paths.VIEWS + "/admin/" + self.options['model_slug'] + "-images-list.blade.php")

        else:
            self.log.emit("No Controller")
            
        self.process_finished(True)

    def logger(self, type):
        if type == "output":
            output = self.process.readAllStandardOutput().data().decode('utf-8-sig', 'ignore')
        else:
            output = self.process.readAllStandardError().data().decode('utf-8-sig', 'ignore')
        self.log.emit(output)

    def process_finished(self, success = True):            
        self.success.emit(success)
        self.finished.emit()