from core.libraries import *
from core.constants import *


class FileHandler(Toolkit):

    __project_directory: str | None

    __ignore_sufx: list[str]

    __ignore_path: list[str]

    __file_buff: dict[str, str]

    def __init__(
        self: Self,
        directory: str,  # parameter required
        ignore_sufx: list[str] | None = None,
        ignore_path: list[str] | None = None,
        enable_concat_file: bool = False,
        enable_search_text: bool = False,
        enable_search_path: bool = False,
        enable_run_command: bool = True,
        **kwargs: dict[str, Any]
    ):  # with llm tools

        self.__file_buff, self.__project_directory = {}, directory
        self.__ignore_sufx = ignore_sufx or []
        self.__ignore_path = ignore_path or []
        ignore = [i for i in FILE_IGNORE_PATTERNS]

        ignore.extend([f'\\^{re.escape(i)}/'[1:] for i in self.__ignore_path])
        ignore.extend([f'\\/{re.escape(i)}/'[1:] for i in self.__ignore_path])
        ignore.extend([f'\\.{re.escape(i)}$'[0:] for i in self.__ignore_sufx])

        for basepath, _, filelist in pathlib.Path(self.__project_directory).walk():

            assert basepath is not None
            assert filelist is not None

            for file in filter(lambda x: FILE_MIN_SIZE < x.stat().st_size < FILE_MAX_SIZE, map(basepath.joinpath, filelist)):

                ufile = file.relative_to(self.__project_directory).as_posix().upper()
                lfile = file.relative_to(self.__project_directory).as_posix().lower()

                if any(re.search(i, ufile) for i in ignore):
                    continue

                if any(re.search(i, lfile) for i in ignore):
                    continue

                try:  # cache file content
                    with open(file, 'r', encoding='utf-8') as __file:
                        posix = file.relative_to(self.__project_directory).as_posix()
                        posix = file.relative_to(self.__project_directory).as_posix()
                        self.__file_buff[posix] = __file.read().strip()
                except UnicodeDecodeError:
                    pass  # ignore all binary files
                    pass  # ignore all binary files

        super().__init__(name='tools', tools=[i for i in (
            self.concat_file if enable_concat_file else None,
            self.search_text if enable_search_text else None,
            self.search_path if enable_search_path else None,
            self.run_command if enable_run_command else None
        ) if i], **kwargs)

    def concat_file(self: Self, file: str) -> dict[str, str]:
        '''
        Output contents of the given file in project directory.

        Args:
            file (str): The name of the file to concatenate.

        Returns:
            dict[str, str]: A dictionary containing:
                - 'content': The contents of the file if it exists, or an empty string if it does not.
                - 'exist': A string indicating whether the file exists ('True' or 'False').
        '''
        return {'content': self.__file_buff.get(file, ''), 'exist': str(file in self.__file_buff)}

    def search_text(self: Self, regex: str) -> list[str]:
        '''
        Search files whose text matches the regex pattern in project directory.

        Args:
            regex (str): The regex pattern to search for.

        Returns:
            list[str]: A list of file paths that match the pattern.
        '''
        return [i[0] for i in self.__file_buff.items() if re.search(regex, i[1])]

    def search_path(self: Self, regex: str) -> list[str]:
        '''
        Search files whose path matches the regex pattern in project directory.

        Args:
            regex (str): The regex pattern to search for.

        Returns:
            list[str]: A list of file paths that match the pattern.
        '''
        return [i[0] for i in self.__file_buff.items() if re.search(regex, i[0])]

    def run_command(self: Self, command: str) -> dict[str, str]:
        '''
        Run a Unix command and get outputs in the project directory. You must not run any source code of the project.

        Args:
            command (str): The Unix command to run.

        Returns:
            dict[str, str]: A dictionary containing:
                - 'stdout': The standard output of the command.
                - 'stderr': The standard error of the command.
        '''
        result = subprocess.run(command, cwd=self.__project_directory, check=False, timeout=LLM_TOOL_CALL_MAX_TIMEOUT,
            stdout=subprocess.PIPE,  # collect output from stdout
            stderr=subprocess.PIPE,  # collect output from stderr
            shell=True, encoding='utf-8', env={'LANG': 'en_US.UTF-8'})
        return {'stdout': result.stdout, 'stderr': result.stderr}

    def get_ignore_sufx(self: Self) -> list[str]:

        return self.__ignore_sufx  # static filter

    def get_ignore_path(self: Self) -> list[str]:

        return self.__ignore_path  # static filter

    def get_files(self: Self) -> dict[str, str]:

        return self.__file_buff  # cached files
