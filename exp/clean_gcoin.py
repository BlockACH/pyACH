import subprocess as sub
import os

def clean_main_directory():
    main_path = os.path.join(os.path.expanduser('~'), '.gcoin/main')
    command_list = ['rm', '-rf', main_path]
    try:
        p = sub.Popen(command_list, stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
    except Exception as e:
        print 'Exception:{}'.format(e)
        return False
    else:
        print 'Output:{}'.format(output)
        print 'Errors:{}'.format(errors)
        return True

clean_main_directory()
# def is_alive(self):
#     try:
#         subprocess.check_call(
#             ['systemctl', 'status', 'gcoin'],
#             stdout=FNULL, stderr=subprocess.STDOUT
#         )
#     except Exception as e:
#         return False
#     else:
#         return True
