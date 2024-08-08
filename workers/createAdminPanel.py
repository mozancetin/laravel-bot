import os
from PyQt5.QtCore import QObject, pyqtSignal, QProcess
from utils import read, write, generate, slug, tab, update_env_variable, copy
import paths

class CreateAdminPanelWorker(QObject):

    log = pyqtSignal(str)
    finished = pyqtSignal()
    success = pyqtSignal(bool)
    
    def __init__(self, path : str, options : dict) -> None:
        super().__init__()
        self.path = path
        self.options = options
        self.model = "Admin"
        self.model_slug = slug(self.model)

    def start(self):
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(lambda: self.logger("output"))
        self.process.readyReadStandardError.connect(lambda: self.logger("error"))
        self.process.finished.connect(self.generate_files)

        self.process.start('cmd')
        self.process.waitForStarted()
        self.log.emit("Process has been started...")
        self.process.write((f"cd {self.path}\n").encode())
        self.process.write((f"php artisan make:model Admin\n").encode())
        self.process.write((f"php artisan make:controller AdminController\n").encode())
        self.process.write((f"php artisan make:middleware AdminMiddleware\n").encode())
        self.process.write((f"composer require intervention/image\n").encode())
        self.process.write((f"composer require spatie/laravel-sitemap:6.4.0\n").encode())
        
        self.process.write(('exit\n').encode())

    def generate_files(self):
        self.log.emit("Updating env variables...")
        update_env_variable(self.path, "DB_DATABASE", slug(self.path.split("/")[-1]))

        self.log.emit("Creating the migration file...")
        write("", self.path + paths.MIGRATION + "create_admin_migration.php")
 
        # Admin Model
        self.log.emit("Generating the admin model...")
        if os.path.exists(paths.TEMPLATES + "models/Admin.txt"):
            admin_model_path = self.path + paths.MODELS + "Admin.php"
            if os.path.exists(admin_model_path):
                if self.options.get("image") == True:
                    generated_text = generate(read(paths.TEMPLATES + "models/Admin.txt"), {"{image_path}" : "'image_path'"})
                else:
                    generated_text = generate(read(paths.TEMPLATES + "models/Admin.txt"), {"{image_path}" : ""})
                
                write(generated_text, admin_model_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + admin_model_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "models/Admin.txt")
            self.process_finished(False)

        # Admin Controller
        self.log.emit("Generating the admin controller...")
        if os.path.exists(paths.TEMPLATES + "controllers/AdminController.txt"):
            admin_controller_path = self.path + paths.CONTROLLERS + "AdminController.php"
            if os.path.exists(admin_controller_path):
                controller_d = {
                    "{image_store_validation}" : "",
                    "{image_store}" : "",
                    "{image_update_validation}" : "",
                    "{image_update}" : "",
                    "{image_destroy}" : ""
                }
                if self.options.get("image") == True:
                    controller_d["{image_store_validation}"] = "'image_path' => 'nullable|image|mimes:jpeg,png,jpg,gif',"
                    controller_d["{image_store}"] = tab(generate(read(paths.SNIPPETS + "image_store.txt"), {"{model_name_slug}": self.model_slug}), 2)
                    controller_d["{image_update_validation}"] = "'image_path' => 'nullable|image|mimes:jpeg,png,jpg,gif',"
                    controller_d["{image_update}"] = tab(generate(read(paths.SNIPPETS + "image_update.txt"), {"{model_name_slug}": self.model_slug}), 2)
                    controller_d["{image_destroy}"] = tab(generate(read(paths.SNIPPETS + "image_destroy.txt"), {"{model_name_slug}": self.model_slug}), 2)

                generated_text = generate(read(paths.TEMPLATES + "controllers/AdminController.txt"), controller_d)
                
                write(generated_text, admin_controller_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + admin_controller_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "controllers/AdminController.txt")
            self.process_finished(False)

        # Admin Migration
        self.log.emit("Generating the admin migration...")
        if os.path.exists(paths.TEMPLATES + "migrations/GeneralMigration.txt"):
            migration_file_path = self.path + paths.MIGRATION + "create_admin_migration.php"
            if os.path.exists(migration_file_path):
                d = dict()
                d["{model_name_slug}"] = self.model_slug
                if self.options.get("image") == True:
                    d["{model_migration}"] = tab(generate(read(paths.SNIPPETS + "admin/admin-migration.txt"), {"{migration_image}":"$table->string('image_path')->nullable();"}), 3)
                else:
                    d["{model_migration}"] = tab(generate(read(paths.SNIPPETS + "admin/admin-migration.txt"), {"{migration_image}":""}), 3)
                generated_migration = generate(read(paths.TEMPLATES + "migrations/GeneralMigration.txt"), d)
                
                write(generated_migration, migration_file_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + migration_file_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "migrations/GeneralMigration.txt")
            self.process_finished(False)

        # Admin Middleware
        self.log.emit("Generating the admin middleware...")
        if os.path.exists(paths.TEMPLATES + "middlewares/AdminMiddleware.txt"):
            middleware_path = self.path + paths.MIDDLEWARE + "AdminMiddleware.php"
            if os.path.exists(middleware_path):
                write(read(paths.TEMPLATES + "middlewares/AdminMiddleware.txt"), middleware_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + middleware_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "middlewares/AdminMiddleware.txt")
            self.process_finished(False)

        # Config Auth
        self.log.emit("Updating config auth...")
        if os.path.exists(paths.TEMPLATES + "auth.txt"):
            auth_path = self.path + paths.CONFIG + "auth.php"
            if os.path.exists(auth_path):
                d = {
                    "{auth_admin_guard}" : tab(read(paths.SNIPPETS + "admin/auth-admin-guard.txt"), 2),
                    "{auth_admin_provider}" : tab(read(paths.SNIPPETS + "admin/auth-admin-provider.txt"), 2)
                }

                generated_text = generate(read(paths.TEMPLATES + "auth.txt"), d)
                write(generated_text, auth_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + auth_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "auth.txt")
            self.process_finished(False)

        # Admin Views
        self.log.emit("Deleting the welcome.blade.php file...")
        if os.path.exists(self.path + paths.VIEWS + "welcome.blade.php"):
            os.remove(self.path + paths.VIEWS + "welcome.blade.php")
            
        self.log.emit("Generating admin views...")
        # admin_layout_path = paths.TEMPLATES + "views/admin/admin-layout.txt"
        admin_dashboard_path = paths.TEMPLATES + "views/admin/dashboard.txt"
        admin_login_path = paths.TEMPLATES + "views/admin/login.txt"
        admin_register_path = paths.TEMPLATES + "views/admin/register.txt"
        admin_register_snippet_path = paths.SNIPPETS + "admin/admin-register-view-image.txt"
        if os.path.exists(admin_dashboard_path) and os.path.exists(admin_login_path) and os.path.exists(admin_register_path) and os.path.exists(admin_register_snippet_path):
            if not os.path.isdir(self.path + paths.VIEWS + "admin"):
                os.mkdir(self.path + paths.VIEWS + "admin")
                
            # layout_path = self.path + paths.VIEWS + "admin/layout.blade.php"
            dashboard_path = self.path + paths.VIEWS + "admin/dashboard.blade.php"
            login_path = self.path + paths.VIEWS + "admin/login.blade.php"
            register_path = self.path + paths.VIEWS + "admin/register.blade.php"
            write(read(admin_dashboard_path), dashboard_path)
            write(read(admin_login_path), login_path)
            # write(generate(read(admin_layout_path), {"{layout_list_items}" : ""}), layout_path)
            if self.options.get("image") == True:
                write(generate(read(admin_register_path), {"{admin_register_image}": tab(read(admin_register_snippet_path), 2)}), register_path)
            else:
                write(generate(read(admin_register_path), {"{admin_register_image}": ""}), register_path)

        else:
            self.log.emit("Some files are missing in /templates/views/admin/")
            self.process_finished(False)

        # Copy css, js and images to the target
        self.log.emit("Copying css, js and images folders")
        if not os.path.isdir(self.path + paths.PUBLIC + "css"):
            os.mkdir(self.path + paths.PUBLIC + "css")

        if not os.path.isdir(self.path + paths.PUBLIC + "js"):
            os.mkdir(self.path + paths.PUBLIC + "js")

        if not os.path.isdir(self.path + paths.PUBLIC + "images"):
            os.mkdir(self.path + paths.PUBLIC + "images")

        copy(paths.LOCALCSS, self.path + paths.PUBLIC + "css")
        copy(paths.LOCALJS, self.path + paths.PUBLIC + "js")
        copy(paths.LOCALIMAGES, self.path + paths.PUBLIC + "images")

        # HTTP Kernel Admin
        self.log.emit("Updating http kernel for admin...")
        if os.path.exists(paths.TEMPLATES + "http_kernel_admin.txt"):
            kernel_path = self.path + paths.HTTP + "kernel.php"
            if os.path.exists(kernel_path):
                write(read(paths.TEMPLATES + "http_kernel_admin.txt"), kernel_path)
            else:
                self.log.emit("Belirtilen yol bulunamadı: " + kernel_path)
                self.process_finished(False)
        else:
            self.log.emit("Belirtilen yol bulunamadı: " + paths.TEMPLATES + "http_kernel_admin.txt")
            self.process_finished(False)

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