import sublime, sublime_plugin
import sys, os, hashlib, threading, time, shutil

ST3 = sublime.version() >= '3000'

EXTENSIONS = {'zip', 'sublime-package', 'epub', 'xmind', 'mmap', 'mmp', 'jar'}

g_subPanelIsOpen = False

def get_temp_dir(fn=None):
    import tempfile
    temp_dir = os.path.join(tempfile.gettempdir(), 'Zip Browser')

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not fn: return temp_dir

    digest = hashlib.md5(fn.encode('utf-8')).hexdigest()
    my_dir = os.path.join(temp_dir, digest)

    if not os.path.exists(my_dir):
        os.makedirs(my_dir)

        with open(os.path.join(my_dir, '.zip_filename'), 'w') as fh:
            fh.write(fn)

    return my_dir


def write_temp_file(zip_filename, filename_in_zip, content):
    #import spdb ; spdb.start()

    temp_dir = get_temp_dir(zip_filename)
    my_dir = os.path.join(temp_dir, *os.path.dirname(filename_in_zip).split('/'))
    if not os.path.exists(my_dir):
        os.makedirs(my_dir)

    filename = os.path.join(temp_dir, *filename_in_zip.split('/'))

    with open(filename, 'wb') as fh:
        fh.write(content)

    return filename


# if 0:
#   class ZipBrowserBrowseCommand(sublime_plugin.TextCommand):

#     def run(self, edit, **kargs):
#         zip_filename = self.view.file_name()

#         if not zip_filename.endswith('.zip'): return

#         import zipfile
#         ziph = zipfile.ZipFile(zip_filename)
#         namelist = ziph.namelist()
#         namelist.sort()
#         panellist = [ f for f in namelist if not f.endswith('/') ]

#         w = self.view.window()

#         if self.mode == 'done':
#             self.mode = None
#             return

#         if self.mode:
#             return

#         if not self.mode:
#             self.mode = 'list'

#         def on_action(index):
#             self.mode = 'done'

#             if index < 0:
#                 self.mode = 'done'
#                 return
                
#             if not self.current_filename: return

#             if index == 1: #open
#                 fn = self.current_filename
#                 fn = write_temp_file(zip_filename, fn, ziph.read(fn))

#                 w.run_command('open_file', {'file': fn})

#             elif index == 2: #remove
#                 fn = self.current_filename

#                 modify_zip_bg(zip_filename, removes = [ self.current_filename ])


#         def on_done(index):
#             self.mode = 'action'

#             self.current_filename = None
#             if index < 0:
#                 self.mode = 'done'
#                 return

#             fn = panellist[index]
#             self.current_filename = fn

#             self.show_panel([
#                     ['Open', self.current_filename],
#                     ['Remove', self.current_filename]
#                 ], on_action)

#         if self.mode == 'list':
#             self.show_panel(panellist, on_done)

def show_subpanel(view, options, callback):
  global g_subPanelIsOpen
  g_subPanelIsOpen = True
  fn = view.file_name()
  
  g_panel.add(fn)
  def _done(index):
      #sys.stderr.write("subpanel done\n")
      global g_subPanelIsOpen
      g_subPanelIsOpen = False
      if callback:
          callback(index)
      try:
          g_panel.remove(fn)
      except:
          pass

  sublime.set_timeout(lambda: view.window().show_quick_panel(options, _done, 0), 10)


def show_panel(view, options, callback):
    fn = view.file_name()

    g_panel.add(fn)
    def _done(index):
        #sys.stderr.write("panel done\n")
        if callback:
            callback(index)
        try:
            g_panel.remove(fn)
        except:
            pass

    sublime.set_timeout(lambda: view.window().show_quick_panel(options, _done, 0), 10)


def select_file_from_zip(view, zip_filename=None, done=None, entries=[]):

    if zip_filename is None:
        zip_filename = self.view.file_name()

    import zipfile
    ziph = zipfile.ZipFile(zip_filename)
    namelist = ziph.namelist()
    namelist.sort()
    panellist = entries + [ f for f in namelist if not f.endswith('/') ]

    if is_panel and not is_panel(view):
        hide_panel()

    show_panel(view, panellist, done(panellist))


class ZipBrowserAction(sublime_plugin.TextCommand):
    command_name = None

    def is_enabled(self):
        return is_valid_zip(self.view.file_name())

    def done(self, filelist):
        def on_done(index):
            if index < 0: return

            self.view.run_command(self.command_name, {'files': filelist[index]})

        return on_done

    def handle_files(self, files):
        if not files:
            select_file_from_zip(self.view, self.view.file_name(), self.done)
            return True

        return False


class ZipBrowserRemoveCommand(ZipBrowserAction):

    command_name = 'zip_browser_remove'

    def run(self, edit, files=[]):
        if self.handle_files(files): return
        zip_filename = self.view.file_name()
        modify_zip_bg(zip_filename,removes=files)


class ZipBrowserOpenCommand(ZipBrowserAction):
    command_name = 'zip_browser_open'

    def run(self, edit, files=[]):
        if self.handle_files(files): return

        zip_filename = self.view.file_name()
        w = self.view.window()

        import zipfile
        ziph = zipfile.ZipFile(zip_filename)
        for fn in files:
            fn = write_temp_file(zip_filename, fn, ziph.read(fn))

            w.open_file(fn)


class ZipBrowserExtractCommand(ZipBrowserAction):

    command_name = 'zip_browser_extract'

    def run(self, edit, files=[], target=None, flat=True):

        if files is True: # extract all files
            files = None

            if flat:
                import zipfile
                ziph = ZipFile(self.view.file_name())
                files = ziph.namelist()

        else:
            if self.handle_files(files): return

        if target is None:
            def on_done(s):
                if not os.path.isabs(s):
                    d = os.path.dirname(self.view.file_name())
                    s = os.path.join(d, s)

                is_dir = os.path.isdir(s)
                if not is_dir and s.endswith('/'):
                    is_dir = True

                if not os.path.exists(s):
                    if is_dir:
                        os.makedirs(s)
                    else:
                        d = os.path.dirname(s)
                        if not os.path.exists(d):
                            os.makedirs(d)

                extract_zip_bg(self.view.file_name(), files, s, flat)
                global g_subPanelIsOpen
                g_subPanelIsOpen = False

            def on_cancel():
              global g_subPanelIsOpen
              g_subPanelIsOpen = False

            entries = ['▶ Custom Folder']

            _entries = {
            }

            for f in self.view.window().folders():
                r = os.path.dirname(f)
                r_len = len(r)
                for d, ds, fs in os.walk(f):
                    entry = d[r_len:].replace('\\', '/')
                    _entries[entry] = d
                    entries.append(entry)

            def on_done_select_target(index):
                if index < 0: return
                if index == 0: 
                    global g_subPanelIsOpen
                    g_subPanelIsOpen = True
                    self.view.window().show_input_panel("Extract to", '', on_done, None, on_cancel)
                else:
                    on_done(_entries[entries[index]])

            show_subpanel(self.view, entries, on_done_select_target)
        else:
            exctract_zip_bg(self.view.file_name(), files, target, flat)

g_default_actions = {}

class ZipBrowserBrowseCommand(ZipBrowserAction):

    def run(self, edit):

        fn = self.view.file_name()

        if fn not in g_default_actions:
            g_default_actions[fn] = ('Open', 'zip_browser_open')

        entries = [
            '▶ Select Action (%s)' % g_default_actions[fn][0],
            '▶ Extract all',
            '▶ Close this View',
        ]

        def on_done(selection):
            def done(index):
                if index < 0:
                    return
                if index == 0: # select action
                    def on_action(index):
                        if index == 0:
                            g_default_actions[fn] = ('Open', 'zip_browser_open')
                        elif index == 1:
                            g_default_actions[fn] = ('Remove', 'zip_browser_remove')
                        elif index == 2:
                            g_default_actions[fn] = ('Extract', 'zip_browser_extract')

                        self.view.run_command('zip_browser_browse')

                    actions = [
                        ['Open', 'Open File from Zip'],
                        ['Remove', 'Remove File from Zip'],
                        ['Extract', 'Extract File from Zip'],
                    ]
                    show_subpanel(self.view, actions, on_action)
                elif index == 1:
                    self.view.run_command('zip_browser_extract', {
                        'files': True, 'flat': False})
                elif index == 2:
                    self.view.window().run_command('close')
                else:
                    self.view.run_command(g_default_actions[fn][1], 
                        {'files': [ selection[index] ]})

            return done

        select_file_from_zip(self.view, fn, on_done, entries=entries)


class ZipBrowserActionCommand(ZipBrowserAction):

    OPEN         = 0
    REMOVE       = 1
    EXTRACT      = 2
    EXTRACT_ALL  = 3

    def run(self, edit, files=None):

        def on_done(index):
            if index < 0: return

            if index == self.OPEN:
                self.view.run_command('zip_browser_open', files=files)

            if index == self.REMOVE:
                self.view.run_command('zip_browser_remove', files=files)

            if index == self.EXTRACT:
                self.view.run_command('zip_browser_extract', files=files)

            if index == self.EXTRACT_ALL:
                self.view.run_command('zip_browser_extract', {'all': True})

        actions = [
            ['Open', 'Open File from Zip'],
            ['Remove', 'Remove File from Zip'],
            ['Extract', 'Extract File from Zip'],
            ]

        if not files:
            actions.append(['Extract All', 'Extract All to Folder'])

        show_subpanel(self.view, actions, on_done)


def modify_zip(zipfname, removes=[], replacements={}):
    # taken from http://stackoverflow.com/questions/4653768/overwriting-file-in-ziparchive
    # modified for replace
    import tempfile, shutil, zipfile
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename in removes: continue

                    if item.filename in replacements:
                        data = replacements[item.filename]
                        zipwrite.writestr(item.filename, data)
                    else:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)

        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)


def extract_zip(zip_filename, files=None, target=None, flat=True):
    import zipfile
    ziph = zipfile.ZipFile(zip_filename)

    if not flat:
        ziph.extractall(path=target, members=files)
    else:
        for f in files:
            with open(os.path.join(target, os.path.basename(f)), 'wb') as fh:
                fh.write(ziph.read(f))

def extract_zip_bg(zip_filename, files=None, target=None, flat=True):
    t = threading.Thread(target=extract_zip, args=(zip_filename,), kwargs=dict(
            files  = files,
            target = target,
            flat   = flat,
        ))
    t.start()

    thread_progress(t, "Extracting files to %s" % target, "Files extracted.")


def thread_progress(*args, **kargs):
    m = __import__('Package Control.package_control.thread_progress', 
        globals  = globals(), 
        locals   = locals(), 
        fromlist = ['ThreadProgress'])
    return m.ThreadProgress(*args, **kargs)


def modify_zip_bg(zip_filename, removes=[], replacements={}):
    t = threading.Thread(target=modify_zip, args=(zip_filename,), kwargs=dict(
            removes = removes,
            replacements = replacements
        ))
    t.start()

    thread_progress(t, "Writing changes to %s" % zip_filename, 
        "%s updated" % zip_filename)
 
def is_valid_zip(filename):
    #print("is_valid_zip: %s" % filename)
    if filename is None or '.' not in filename: return False
    return filename.rsplit('.', 1)[1] in EXTENSIONS

g_panel = set()
def is_panel(view=None):
    if view is None:
        return len(g_panel)

    return view.file_name() in g_panel

def hide_panel():
    #sys.stderr.write('hide_overlay\n')
    sublime.active_window().run_command("hide_overlay")
    #time.sleep(0.1)
    g_panel.clear()

class ZipBrowserEventListener(sublime_plugin.EventListener):

    def on_load(self, view):
        if not is_valid_zip(view.file_name()):
          if is_panel():
            hide_panel()
          return
        self._deferred(view)


    def _deferred(self, view):
        current_id = view.id()

        def do_activate():
            if g_subPanelIsOpen: return

            if current_id != sublime.active_window().active_view().id(): return

            if not is_panel(view):
                view.run_command('zip_browser_browse')

        sublime.set_timeout(do_activate, 600)

    def on_activated(self, activated_view):
        w = activated_view.window()
        if not w: return
        
        view = activated_view.window().active_view()

        if not is_valid_zip(view.file_name()):
            #sys.stderr.write("activated: %s, %s\n" % (view.file_name(), view.name()))

            if is_panel():
                hide_panel()
            return
           
        self._deferred(view)

    #def on_deactivated(self, view):
        #if is_valid_zip(view.file_name()):
            #if is_panel():
                #hide_panel()
#

    def on_post_save(self, view):
        temp_dir = get_temp_dir()
        fn = view.file_name()
        if not fn.startswith(temp_dir): return

        #import spdb ; spdb.start()

        md5, filename = fn[len(temp_dir)+1:].replace('\\', '/').split('/', 1)

        my_zipfile_info = os.path.join(temp_dir, md5, '.zip_filename')
        with open(my_zipfile_info, 'r') as fh:
            zip_filename = fh.read().strip()

        with open(fn, 'rb') as fh:
            content = fh.read()

        modify_zip_bg(zip_filename, replacements={filename: content})


def cleanup_temp_dir():

    age = time.time() - 3600
    for root, dirs, files in os.walk(get_temp_dir(), topdown=False):
        if dirs:
            for d in dirs:
                dn = os.path.join(root, d)
                if age > os.path.getmtime(dn):
                    shutil.rmtree(dn)

        if files:
            for f in files:
                fn = os.path.join(root, f)
                if age > os.path.getmtime(fn):
                    os.remove(fn)

    sublime.set_timeout(cleanup_temp_dir, 3600000)

def plugin_loaded():
    try:
        cache_dir = os.path.join(sublime.cache_path(), 'Zip Browser')
    except:
        cache_dir = os.path.join(sublime.packages_path(), '..', 'Cache', 'Zip Browser')

    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    cleanup_temp_dir()


if not ST3:
    plugin_loaded()

