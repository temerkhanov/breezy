/* Generated by Pyrex 0.9.6.4 on Wed Aug 20 12:04:52 2008 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"
#ifndef PY_LONG_LONG
  #define PY_LONG_LONG LONG_LONG
#endif
#if PY_VERSION_HEX < 0x02050000
  typedef int Py_ssize_t;
  #define PY_SSIZE_T_MAX INT_MAX
  #define PY_SSIZE_T_MIN INT_MIN
  #define PyInt_FromSsize_t(z) PyInt_FromLong(z)
  #define PyInt_AsSsize_t(o)	PyInt_AsLong(o)
#endif
#ifndef WIN32
  #ifndef __stdcall
    #define __stdcall
  #endif
  #ifndef __cdecl
    #define __cdecl
  #endif
#endif
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif
#include <math.h>
#include "errno.h"
#include "sys/types.h"
#include "dirent.h"
#include "readdir.h"


typedef struct {PyObject **p; char *s;} __Pyx_InternTabEntry; /*proto*/
typedef struct {PyObject **p; char *s; long n;} __Pyx_StringTabEntry; /*proto*/

static PyObject *__pyx_m;
static PyObject *__pyx_b;
static int __pyx_lineno;
static char *__pyx_filename;
static char **__pyx_f;

static char __pyx_mdoc[] = "Wrapper for readdir which grabs file type from d_type.";

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list); /*proto*/

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name); /*proto*/

static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb); /*proto*/

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t); /*proto*/

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t); /*proto*/

static void __Pyx_AddTraceback(char *funcname); /*proto*/

/* Declarations from readdir */



/* Implementation of readdir */

static char __pyx_k11[] = ".";

static PyObject *__pyx_n_os;
static PyObject *__pyx_n_sys;
static PyObject *__pyx_n__directory;
static PyObject *__pyx_n_directory;
static PyObject *__pyx_n__chardev;
static PyObject *__pyx_n_chardev;
static PyObject *__pyx_n__block;
static PyObject *__pyx_n_block;
static PyObject *__pyx_n__file;
static PyObject *__pyx_n_file;
static PyObject *__pyx_n__fifo;
static PyObject *__pyx_n_fifo;
static PyObject *__pyx_n__symlink;
static PyObject *__pyx_n_symlink;
static PyObject *__pyx_n__socket;
static PyObject *__pyx_n_socket;
static PyObject *__pyx_n__unknown;
static PyObject *__pyx_n_unknown;
static PyObject *__pyx_n_ord;
static PyObject *__pyx_n_dot;

static PyObject *__pyx_k11p;

static PyObject *__pyx_n_OSError;
static PyObject *__pyx_n_append;


static PyObject *__pyx_f_7readdir_read_dir(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_7readdir_read_dir[] = "Like os.listdir, this reads a directories contents.\n\n    :param path: the directory to list.\n    :return: a list of (basename, kind) tuples.\n    ";
static PyObject *__pyx_f_7readdir_read_dir(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_path = 0;
  DIR *__pyx_v_the_dir;
  dirent *__pyx_v_entry;
  dirent __pyx_v_sentinel;
  char *__pyx_v_name;
  PyObject *__pyx_v_result;
  PyObject *__pyx_v_type;
  PyObject *__pyx_r;
  char *__pyx_1;
  int __pyx_2;
  PyObject *__pyx_3 = 0;
  PyObject *__pyx_4 = 0;
  PyObject *__pyx_5 = 0;
  PyObject *__pyx_6 = 0;
  int __pyx_7;
  static char *__pyx_argnames[] = {"path",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_path)) return 0;
  Py_INCREF(__pyx_v_path);
  __pyx_v_result = Py_None; Py_INCREF(Py_None);
  __pyx_v_type = Py_None; Py_INCREF(Py_None);

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":82 */
  __pyx_1 = PyString_AsString(__pyx_v_path); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 82; goto __pyx_L1;}
  __pyx_v_the_dir = opendir(__pyx_1);

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":83 */
  __pyx_2 = (NULL == __pyx_v_the_dir);
  if (__pyx_2) {
    __pyx_3 = __Pyx_GetName(__pyx_b, __pyx_n_OSError); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    __pyx_4 = PyInt_FromLong(errno); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    __pyx_5 = PyString_FromString(strerror(errno)); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    __pyx_6 = PyTuple_New(2); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    PyTuple_SET_ITEM(__pyx_6, 0, __pyx_4);
    PyTuple_SET_ITEM(__pyx_6, 1, __pyx_5);
    __pyx_4 = 0;
    __pyx_5 = 0;
    __pyx_4 = PyObject_CallObject(__pyx_3, __pyx_6); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_6); __pyx_6 = 0;
    __Pyx_Raise(__pyx_4, 0, 0);
    Py_DECREF(__pyx_4); __pyx_4 = 0;
    {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
    goto __pyx_L2;
  }
  __pyx_L2:;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":85 */
  __pyx_5 = PyList_New(0); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 85; goto __pyx_L1;}
  Py_DECREF(__pyx_v_result);
  __pyx_v_result = __pyx_5;
  __pyx_5 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":86 */
  /*try:*/ {

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":87 */
    __pyx_v_entry = (&__pyx_v_sentinel);

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":88 */
    while (1) {
      __pyx_2 = (__pyx_v_entry != NULL);
      if (!__pyx_2) break;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":89 */
      __pyx_v_entry = readdir(__pyx_v_the_dir);

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":90 */
      __pyx_2 = (__pyx_v_entry == NULL);
      if (__pyx_2) {
        __pyx_2 = (errno == EAGAIN);
        if (__pyx_2) {
          goto __pyx_L6;
          goto __pyx_L9;
        }
        __pyx_2 = (errno != ENOTDIR);
        if (__pyx_2) {
          __pyx_2 = (errno != ENOENT);
          if (__pyx_2) {
            __pyx_2 = (errno != 0);
          }
        }
        if (__pyx_2) {
          __pyx_3 = __Pyx_GetName(__pyx_b, __pyx_n_OSError); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          __pyx_6 = PyInt_FromLong(errno); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          __pyx_4 = PyString_FromString(strerror(errno)); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          __pyx_5 = PyTuple_New(2); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          PyTuple_SET_ITEM(__pyx_5, 0, __pyx_6);
          PyTuple_SET_ITEM(__pyx_5, 1, __pyx_4);
          __pyx_6 = 0;
          __pyx_4 = 0;
          __pyx_6 = PyObject_CallObject(__pyx_3, __pyx_5); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          Py_DECREF(__pyx_3); __pyx_3 = 0;
          Py_DECREF(__pyx_5); __pyx_5 = 0;
          __Pyx_Raise(__pyx_6, 0, 0);
          Py_DECREF(__pyx_6); __pyx_6 = 0;
          {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L4;}
          goto __pyx_L9;
        }
        /*else*/ {
          goto __pyx_L6;
        }
        __pyx_L9:;
        goto __pyx_L8;
      }
      __pyx_L8:;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":104 */
      __pyx_v_name = __pyx_v_entry->d_name;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":105 */
      __pyx_4 = PyInt_FromLong((__pyx_v_name[0])); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 105; goto __pyx_L4;}
      __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n_dot); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 105; goto __pyx_L4;}
      if (PyObject_Cmp(__pyx_4, __pyx_3, &__pyx_2) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 105; goto __pyx_L4;}
      __pyx_2 = __pyx_2 == 0;
      Py_DECREF(__pyx_4); __pyx_4 = 0;
      Py_DECREF(__pyx_3); __pyx_3 = 0;
      if (__pyx_2) {
        __pyx_2 = ((__pyx_v_name[1]) == 0);
        if (!__pyx_2) {
          __pyx_5 = PyInt_FromLong((__pyx_v_name[1])); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L4;}
          __pyx_6 = __Pyx_GetName(__pyx_m, __pyx_n_dot); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L4;}
          if (PyObject_Cmp(__pyx_5, __pyx_6, &__pyx_2) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L4;}
          __pyx_2 = __pyx_2 == 0;
          Py_DECREF(__pyx_5); __pyx_5 = 0;
          Py_DECREF(__pyx_6); __pyx_6 = 0;
          if (__pyx_2) {
            __pyx_2 = ((__pyx_v_name[2]) == 0);
          }
        }
      }
      __pyx_7 = (!__pyx_2);
      if (__pyx_7) {

        /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":109 */
        __pyx_2 = (__pyx_v_entry->d_type == DT_UNKNOWN);
        if (__pyx_2) {
          __pyx_4 = __Pyx_GetName(__pyx_m, __pyx_n__unknown); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_4;
          __pyx_4 = 0;
          goto __pyx_L11;
        }
        __pyx_7 = (__pyx_v_entry->d_type == DT_REG);
        if (__pyx_7) {
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__file); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 112; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L11;
        }
        __pyx_2 = (__pyx_v_entry->d_type == DT_DIR);
        if (__pyx_2) {
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__directory); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 114; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
          goto __pyx_L11;
        }
        __pyx_7 = (__pyx_v_entry->d_type == DT_FIFO);
        if (__pyx_7) {
          __pyx_6 = __Pyx_GetName(__pyx_m, __pyx_n__fifo); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 116; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_6;
          __pyx_6 = 0;
          goto __pyx_L11;
        }
        __pyx_2 = (__pyx_v_entry->d_type == DT_SOCK);
        if (__pyx_2) {
          __pyx_4 = __Pyx_GetName(__pyx_m, __pyx_n__socket); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 118; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_4;
          __pyx_4 = 0;
          goto __pyx_L11;
        }
        __pyx_7 = (__pyx_v_entry->d_type == DT_CHR);
        if (__pyx_7) {
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__chardev); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 120; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L11;
        }
        __pyx_2 = (__pyx_v_entry->d_type == DT_BLK);
        if (__pyx_2) {
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__block); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 122; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
          goto __pyx_L11;
        }
        /*else*/ {
          __pyx_6 = __Pyx_GetName(__pyx_m, __pyx_n__unknown); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 124; goto __pyx_L4;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_6;
          __pyx_6 = 0;
        }
        __pyx_L11:;

        /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":126 */
        __pyx_4 = PyObject_GetAttr(__pyx_v_result, __pyx_n_append); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 126; goto __pyx_L4;}
        __pyx_3 = PyString_FromString(__pyx_v_entry->d_name); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 126; goto __pyx_L4;}
        __pyx_5 = PyTuple_New(2); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 126; goto __pyx_L4;}
        PyTuple_SET_ITEM(__pyx_5, 0, __pyx_3);
        Py_INCREF(__pyx_n_unknown);
        PyTuple_SET_ITEM(__pyx_5, 1, __pyx_n_unknown);
        __pyx_3 = 0;
        __pyx_6 = PyTuple_New(1); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 126; goto __pyx_L4;}
        PyTuple_SET_ITEM(__pyx_6, 0, __pyx_5);
        __pyx_5 = 0;
        __pyx_3 = PyObject_CallObject(__pyx_4, __pyx_6); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 126; goto __pyx_L4;}
        Py_DECREF(__pyx_4); __pyx_4 = 0;
        Py_DECREF(__pyx_6); __pyx_6 = 0;
        Py_DECREF(__pyx_3); __pyx_3 = 0;
        goto __pyx_L10;
      }
      __pyx_L10:;
      __pyx_L6:;
    }
  }
  /*finally:*/ {
    int __pyx_why;
    PyObject *__pyx_exc_type, *__pyx_exc_value, *__pyx_exc_tb;
    int __pyx_exc_lineno;
    __pyx_why = 0; goto __pyx_L5;
    __pyx_L4: {
      __pyx_why = 4;
      Py_XDECREF(__pyx_5); __pyx_5 = 0;
      Py_XDECREF(__pyx_4); __pyx_4 = 0;
      Py_XDECREF(__pyx_6); __pyx_6 = 0;
      Py_XDECREF(__pyx_3); __pyx_3 = 0;
      PyErr_Fetch(&__pyx_exc_type, &__pyx_exc_value, &__pyx_exc_tb);
      __pyx_exc_lineno = __pyx_lineno;
      goto __pyx_L5;
    }
    __pyx_L5:;
    __pyx_7 = ((-1) == closedir(__pyx_v_the_dir));
    if (__pyx_7) {
      __pyx_5 = __Pyx_GetName(__pyx_b, __pyx_n_OSError); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      __pyx_4 = PyInt_FromLong(errno); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      __pyx_6 = PyString_FromString(strerror(errno)); if (!__pyx_6) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      __pyx_3 = PyTuple_New(2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      PyTuple_SET_ITEM(__pyx_3, 0, __pyx_4);
      PyTuple_SET_ITEM(__pyx_3, 1, __pyx_6);
      __pyx_4 = 0;
      __pyx_6 = 0;
      __pyx_4 = PyObject_CallObject(__pyx_5, __pyx_3); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      Py_DECREF(__pyx_5); __pyx_5 = 0;
      Py_DECREF(__pyx_3); __pyx_3 = 0;
      __Pyx_Raise(__pyx_4, 0, 0);
      Py_DECREF(__pyx_4); __pyx_4 = 0;
      {__pyx_filename = __pyx_f[0]; __pyx_lineno = 129; goto __pyx_L12;}
      goto __pyx_L13;
    }
    __pyx_L13:;
    goto __pyx_L14;
    __pyx_L12:;
    if (__pyx_why == 4) {
      Py_XDECREF(__pyx_exc_type);
      Py_XDECREF(__pyx_exc_value);
      Py_XDECREF(__pyx_exc_tb);
    }
    goto __pyx_L1;
    __pyx_L14:;
    switch (__pyx_why) {
      case 4: {
        PyErr_Restore(__pyx_exc_type, __pyx_exc_value, __pyx_exc_tb);
        __pyx_lineno = __pyx_exc_lineno;
        __pyx_exc_type = 0;
        __pyx_exc_value = 0;
        __pyx_exc_tb = 0;
        goto __pyx_L1;
      }
    }
  }

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":130 */
  Py_INCREF(__pyx_v_result);
  __pyx_r = __pyx_v_result;
  goto __pyx_L0;

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_3);
  Py_XDECREF(__pyx_4);
  Py_XDECREF(__pyx_5);
  Py_XDECREF(__pyx_6);
  __Pyx_AddTraceback("readdir.read_dir");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v_result);
  Py_DECREF(__pyx_v_type);
  Py_DECREF(__pyx_v_path);
  return __pyx_r;
}

static __Pyx_InternTabEntry __pyx_intern_tab[] = {
  {&__pyx_n_OSError, "OSError"},
  {&__pyx_n__block, "_block"},
  {&__pyx_n__chardev, "_chardev"},
  {&__pyx_n__directory, "_directory"},
  {&__pyx_n__fifo, "_fifo"},
  {&__pyx_n__file, "_file"},
  {&__pyx_n__socket, "_socket"},
  {&__pyx_n__symlink, "_symlink"},
  {&__pyx_n__unknown, "_unknown"},
  {&__pyx_n_append, "append"},
  {&__pyx_n_block, "block"},
  {&__pyx_n_chardev, "chardev"},
  {&__pyx_n_directory, "directory"},
  {&__pyx_n_dot, "dot"},
  {&__pyx_n_fifo, "fifo"},
  {&__pyx_n_file, "file"},
  {&__pyx_n_ord, "ord"},
  {&__pyx_n_os, "os"},
  {&__pyx_n_socket, "socket"},
  {&__pyx_n_symlink, "symlink"},
  {&__pyx_n_sys, "sys"},
  {&__pyx_n_unknown, "unknown"},
  {0, 0}
};

static __Pyx_StringTabEntry __pyx_string_tab[] = {
  {&__pyx_k11p, __pyx_k11, sizeof(__pyx_k11)},
  {0, 0, 0}
};

static struct PyMethodDef __pyx_methods[] = {
  {"read_dir", (PyCFunction)__pyx_f_7readdir_read_dir, METH_VARARGS|METH_KEYWORDS, __pyx_doc_7readdir_read_dir},
  {0, 0, 0, 0}
};

static void __pyx_init_filenames(void); /*proto*/

PyMODINIT_FUNC initreaddir(void); /*proto*/
PyMODINIT_FUNC initreaddir(void) {
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  PyObject *__pyx_3 = 0;
  __pyx_init_filenames();
  __pyx_m = Py_InitModule4("readdir", __pyx_methods, __pyx_mdoc, 0, PYTHON_API_VERSION);
  if (!__pyx_m) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;};
  Py_INCREF(__pyx_m);
  __pyx_b = PyImport_AddModule("__builtin__");
  if (!__pyx_b) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;};
  if (PyObject_SetAttrString(__pyx_m, "__builtins__", __pyx_b) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;};
  if (__Pyx_InternStrings(__pyx_intern_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;};
  if (__Pyx_InitStrings(__pyx_string_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;};

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":20 */
  __pyx_1 = __Pyx_Import(__pyx_n_os, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 20; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_os, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 20; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":21 */
  __pyx_1 = __Pyx_Import(__pyx_n_sys, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_sys, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":55 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__directory, __pyx_n_directory) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 55; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":56 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__chardev, __pyx_n_chardev) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 56; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":57 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__block, __pyx_n_block) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 57; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":58 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__file, __pyx_n_file) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 58; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":59 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__fifo, __pyx_n_fifo) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 59; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":60 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__symlink, __pyx_n_symlink) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 60; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":61 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__socket, __pyx_n_socket) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 61; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":62 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__unknown, __pyx_n_unknown) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 62; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":64 */
  __pyx_1 = __Pyx_GetName(__pyx_b, __pyx_n_ord); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  __pyx_2 = PyTuple_New(1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_INCREF(__pyx_k11p);
  PyTuple_SET_ITEM(__pyx_2, 0, __pyx_k11p);
  __pyx_3 = PyObject_CallObject(__pyx_1, __pyx_2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  if (PyObject_SetAttr(__pyx_m, __pyx_n_dot, __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":70 */
  return;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("readdir");
}

static char *__pyx_filenames[] = {
  "readdir.pyx",
};

/* Runtime support code */

static void __pyx_init_filenames(void) {
  __pyx_f = __pyx_filenames;
}

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list) {
    PyObject *__import__ = 0;
    PyObject *empty_list = 0;
    PyObject *module = 0;
    PyObject *global_dict = 0;
    PyObject *empty_dict = 0;
    PyObject *list;
    __import__ = PyObject_GetAttrString(__pyx_b, "__import__");
    if (!__import__)
        goto bad;
    if (from_list)
        list = from_list;
    else {
        empty_list = PyList_New(0);
        if (!empty_list)
            goto bad;
        list = empty_list;
    }
    global_dict = PyModule_GetDict(__pyx_m);
    if (!global_dict)
        goto bad;
    empty_dict = PyDict_New();
    if (!empty_dict)
        goto bad;
    module = PyObject_CallFunction(__import__, "OOOO",
        name, global_dict, empty_dict, list);
bad:
    Py_XDECREF(empty_list);
    Py_XDECREF(__import__);
    Py_XDECREF(empty_dict);
    return module;
}

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name) {
    PyObject *result;
    result = PyObject_GetAttr(dict, name);
    if (!result)
        PyErr_SetObject(PyExc_NameError, name);
    return result;
}

static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb) {
    Py_XINCREF(type);
    Py_XINCREF(value);
    Py_XINCREF(tb);
    /* First, check the traceback argument, replacing None with NULL. */
    if (tb == Py_None) {
        Py_DECREF(tb);
        tb = 0;
    }
    else if (tb != NULL && !PyTraceBack_Check(tb)) {
        PyErr_SetString(PyExc_TypeError,
            "raise: arg 3 must be a traceback or None");
        goto raise_error;
    }
    /* Next, replace a missing value with None */
    if (value == NULL) {
        value = Py_None;
        Py_INCREF(value);
    }
    #if PY_VERSION_HEX < 0x02050000
    if (!PyClass_Check(type))
    #else
    if (!PyType_Check(type))
    #endif
    {
        /* Raising an instance.  The value should be a dummy. */
        if (value != Py_None) {
            PyErr_SetString(PyExc_TypeError,
                "instance exception may not have a separate value");
            goto raise_error;
        }
        /* Normalize to raise <class>, <instance> */
        Py_DECREF(value);
        value = type;
        #if PY_VERSION_HEX < 0x02050000
            if (PyInstance_Check(type)) {
                type = (PyObject*) ((PyInstanceObject*)type)->in_class;
                Py_INCREF(type);
            }
            else {
                PyErr_SetString(PyExc_TypeError,
                    "raise: exception must be an old-style class or instance");
                goto raise_error;
            }
        #else
            type = (PyObject*) type->ob_type;
            Py_INCREF(type);
            if (!PyType_IsSubtype((PyTypeObject *)type, (PyTypeObject *)PyExc_BaseException)) {
                PyErr_SetString(PyExc_TypeError,
                    "raise: exception class must be a subclass of BaseException");
                goto raise_error;
            }
        #endif
    }
    PyErr_Restore(type, value, tb);
    return;
raise_error:
    Py_XDECREF(value);
    Py_XDECREF(type);
    Py_XDECREF(tb);
    return;
}

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t) {
    while (t->p) {
        *t->p = PyString_InternFromString(t->s);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t) {
    while (t->p) {
        *t->p = PyString_FromStringAndSize(t->s, t->n - 1);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

#include "compile.h"
#include "frameobject.h"
#include "traceback.h"

static void __Pyx_AddTraceback(char *funcname) {
    PyObject *py_srcfile = 0;
    PyObject *py_funcname = 0;
    PyObject *py_globals = 0;
    PyObject *empty_tuple = 0;
    PyObject *empty_string = 0;
    PyCodeObject *py_code = 0;
    PyFrameObject *py_frame = 0;
    
    py_srcfile = PyString_FromString(__pyx_filename);
    if (!py_srcfile) goto bad;
    py_funcname = PyString_FromString(funcname);
    if (!py_funcname) goto bad;
    py_globals = PyModule_GetDict(__pyx_m);
    if (!py_globals) goto bad;
    empty_tuple = PyTuple_New(0);
    if (!empty_tuple) goto bad;
    empty_string = PyString_FromString("");
    if (!empty_string) goto bad;
    py_code = PyCode_New(
        0,            /*int argcount,*/
        0,            /*int nlocals,*/
        0,            /*int stacksize,*/
        0,            /*int flags,*/
        empty_string, /*PyObject *code,*/
        empty_tuple,  /*PyObject *consts,*/
        empty_tuple,  /*PyObject *names,*/
        empty_tuple,  /*PyObject *varnames,*/
        empty_tuple,  /*PyObject *freevars,*/
        empty_tuple,  /*PyObject *cellvars,*/
        py_srcfile,   /*PyObject *filename,*/
        py_funcname,  /*PyObject *name,*/
        __pyx_lineno,   /*int firstlineno,*/
        empty_string  /*PyObject *lnotab*/
    );
    if (!py_code) goto bad;
    py_frame = PyFrame_New(
        PyThreadState_Get(), /*PyThreadState *tstate,*/
        py_code,             /*PyCodeObject *code,*/
        py_globals,          /*PyObject *globals,*/
        0                    /*PyObject *locals*/
    );
    if (!py_frame) goto bad;
    py_frame->f_lineno = __pyx_lineno;
    PyTraceBack_Here(py_frame);
bad:
    Py_XDECREF(py_srcfile);
    Py_XDECREF(py_funcname);
    Py_XDECREF(empty_tuple);
    Py_XDECREF(empty_string);
    Py_XDECREF(py_code);
    Py_XDECREF(py_frame);
}
