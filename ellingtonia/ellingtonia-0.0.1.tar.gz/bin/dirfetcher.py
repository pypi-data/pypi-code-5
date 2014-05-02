import os
import sys
import jinja2

# path = sys.argv[1]



def get_context(dirpath):
    context = {
        'clients': []
    }

    for client in os.listdir(dirpath):
        c = {
            "name": client,
            "projects": []
        }
        projects = []
        projpath = dirpath+client
      # for project in os.listdir('docs_in_test/%s' % client):
        for project in os.listdir(projpath):
            c['projects'].append({
                # 'client': client,
                'name': project,
                'url': projpath+'/'+project+'/index.html'
            })
        context['clients'].append(c)
    print context
    # return context


def jinja_messenger():
    # def jinja_messenger(object, jinjafile_addr):
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "/home/song/Workspaces/ellingtonia/templates/example1.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    templateVars = get_context(path)
    f = open('/home/song/Workspaces/ellingtonia/outputs/output.html', 'w')
    f.write(template.render(templateVars))
    f.close()
    print get_context(path)

# jinja_messenger()
# get_context(sys.argv[1])