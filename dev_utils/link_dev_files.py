import os
import platform
from argparse import ArgumentParser
from pathlib import Path


class InstallFiles:
    @staticmethod
    def get_src_dir(name):
        return Path(__file__).parent.parent / "src" / "dvr_smart_edit" / "data" / name

    @staticmethod
    def get_dvr_program_data_dir():
        current_os = platform.system()

        if current_os == "Windows":
            return Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Blackmagic Design" / "DaVinci Resolve"
        elif current_os == "Darwin":  # mac
            return Path.home() / "Library" / "Application Support" / "Blackmagic Design" / "DaVinci Resolve"
        else:  # linux
            return Path.home() / ".local" / "share" / "DaVinciResolve"


class Main:
    def __init__(self):
        argparser = ArgumentParser()
        argparser.add_argument("--force", "-f", action="store_true")
        args = argparser.parse_args()

        self.force = args.force
        self.install_files()

    def install_files(self):
        print(f"[dvr_smart_edit] Installing DaVinci Resolve plugin files")

        self.create_symlink(
            InstallFiles.get_src_dir("fuses"),
            InstallFiles.get_dvr_program_data_dir() / "Fusion" / "Fuses" / "SmartEdit",
        )
        self.create_symlink(
            InstallFiles.get_src_dir("scripts"),
            InstallFiles.get_dvr_program_data_dir() / "Fusion" / "Scripts" / "Edit" / "SmartEdit",
        )
        self.create_symlink(
            InstallFiles.get_src_dir("macros/Generators"),
            InstallFiles.get_dvr_program_data_dir() / "Fusion" / "Templates" / "Edit" / "Generators" / "SmartEdit",
        )
        self.create_symlink(
            InstallFiles.get_src_dir("macros/Titles"),
            InstallFiles.get_dvr_program_data_dir() / "Fusion" / "Templates" / "Edit" / "Titles" / "SmartEdit",
        )

    def create_symlink(self, src_dir, dst_dir):
        if not dst_dir.exists() and not dst_dir.is_symlink():
            dst_dir.symlink_to(src_dir, target_is_directory=True)
            print(f"[dvr_smart_edit] Created link `{dst_dir}`")
        elif self.force:
            dst_dir.unlink()
            dst_dir.symlink_to(src_dir, target_is_directory=True)
            print(f"[dvr_smart_edit] Created link `{dst_dir}`")
        else:
            print(f"[dvr_smart_edit] Cannot create link `{dst_dir}` (already exists)")


if __name__ == "__main__":
    Main()
