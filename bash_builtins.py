import sys
import re
import os
import argparse
import threading


class BuiltinThreadWrapper:
    """
    wraps Thread object. Adds to it wait() method
    """

    def __init__(self, thread_object):
        self.thread = thread_object

    def wait(self):
        self.thread.join()


### BUILTIN_FUNCTIONS

def cat_function(args, stdin, stdout):
    parser = argparse.ArgumentParser(prog="cat", description='print file content')
    parser.add_argument("FILE", help='path to file')
    parsed_args = parser.parse_args(args)
    fin = open(vars(parsed_args).get("FILE"))
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(fin.read() + "\n")


def echo_function(args, stdin, stdout):
    parser = argparse.ArgumentParser(prog="echo", description='print arguments')
    parser.add_argument("argument", nargs='+')
    parsed_args = parser.parse_args(args)
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(' '.join(vars(parsed_args).get("argument")) + "\n")


def wc_function(args, stdin, stdout):
    parser = argparse.ArgumentParser(prog="wc", description='print number of lines, words and bytes in FILE')
    parser.add_argument("FILE", help='path to file')
    parsed_args = parser.parse_args(args)
    filepath = vars(parsed_args).get("FILE")
    fin = open(filepath)
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    lines = fin.readlines()
    words_count = sum([len(line.split()) for line in lines])
    file_size = os.path.getsize(filepath)
    fout.write(str(len(lines)) + " " + str(words_count) + " " + str(file_size) + "\n")


def pwd_function(args, stdin, stdout):
    parser = argparse.ArgumentParser(prog="pwd", description='print current directory')
    parser.parse_args(args)
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(os.getcwd() + "\n")


def exit_function(args, stdin, stdout):
    sys.exit(0);


command_to_function = {
    "cat": cat_function,
    "echo": echo_function,
    "wc": wc_function,
    "pwd": pwd_function,
    "exit": exit_function
}


def simple_interprete_single_builtin_command(command, stdin, stdout):
    """
    execute single(without pipes) builtin command with stdin=stdin, stdout=stdout

    :param stdout: output file descriptor
    :param stdin: input file descriptor
    :param command: list of attributes of command
    :return: Object with .wait(), None if command unrecognized
    """
    if len(command) == 0:
        class EmptyCommand:
            def wait(self):
                pass

        return EmptyCommand()

    equality_match = re.match(r"^([\w]+)=(.+)$", command[0])
    if equality_match:
        os.environ[equality_match.group(1)] = equality_match.group(2)

        class Equality:
            def wait(self):
                pass

        return Equality()
    elif command[0] in command_to_function:
        thread = threading.Thread(target=command_to_function.get(command[0]), args=(command[1:], stdin, stdout))
        thread.start()

        return BuiltinThreadWrapper(thread)
    else:
        return None
