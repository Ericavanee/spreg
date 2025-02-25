"""Internal helper files for user output."""

__author__ = (
    "Luc Anselin luc.anselin@asu.edu, "
    "David C. Folch david.folch@asu.edu, "
    "Levi John Wolf levi.john.wolf@gmail.com, "
    "Jing Yao jingyao@asu.edu"
)
import numpy as np
import copy as COPY
from . import diagnostics
from . import sputils as spu
from libpysal import weights
from scipy.sparse.csr import csr_matrix


def set_name_ds(name_ds):
    """Set the dataset name in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------

    name_ds     : string
                  User provided dataset name.

    Returns
    -------

    name_ds     : string

    """
    if not name_ds:
        name_ds = "unknown"
    return name_ds


def set_name_y(name_y):
    """Set the dataset name in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_ds     : string
                  User provided dataset name.

    Returns
    -------
    name_ds     : string

    """
    if not name_y:
        name_y = "dep_var"
    return name_y


def set_name_x(name_x, x, constant=False):
    """Set the independent variable names in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_x      : list of string
                  User provided exogenous variable names.

    x           : array
                  User provided exogenous variables including the constant.
    constant    : boolean
                  If False (default), constant name not included in name_x list yet
                  Append 'CONSTANT' at the front of the names

    Returns
    -------
    name_x      : list of strings

    """
    if not name_x:
        name_x = ["var_" + str(i + 1) for i in range(x.shape[1] - 1 + int(constant))]
    else:
        name_x = name_x[:]
    if not constant:
        name_x.insert(0, "CONSTANT")
    return name_x


def set_name_yend(name_yend, yend):
    """Set the endogenous variable names in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_yend   : list of strings
                  User provided exogenous variable names.

    Returns
    -------
    name_yend   : list of strings

    """
    if yend is not None:
        if not name_yend:
            return ["endogenous_" + str(i + 1) for i in range(len(yend[0]))]
        else:
            return name_yend[:]
    else:
        return []


def set_name_q(name_q, q):
    """Set the external instrument names in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_q      : string
                  User provided instrument names.
    q           : array
                  Array of instruments

    Returns
    -------
    name_q      : list of strings

    """
    if q is not None:
        if not name_q:
            return ["instrument_" + str(i + 1) for i in range(len(q[0]))]
        else:
            return name_q[:]
    else:
        return []


def set_name_yend_sp(name_y):
    """Set the spatial lag name in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_y      : string
                  User provided dependent variable name.

    Returns
    -------
    name_yend_sp : string

    """
    return "W_" + name_y


def set_name_q_sp(name_x, w_lags, name_q, lag_q, force_all=False):
    """Set the spatial instrument names in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_x      : list of strings
                  User provided exogenous variable names.
    w_lags      : int
                  User provided number of spatial instruments lags

    Returns
    -------
    name_q_sp   : list of strings

    """
    if force_all:
        names = name_x
    else:
        names = name_x[1:]  # drop the constant
    if lag_q:
        names = names + name_q
    sp_inst_names = []
    for j in names:
        sp_inst_names.append("W_" + j)
    if w_lags > 1:
        for i in range(2, w_lags + 1):
            for j in names:
                sp_inst_names.append("W" + str(i) + "_" + j)
    return sp_inst_names


def set_name_h(name_x, name_q):
    """Set the full instruments names in regression; return generic name if user
    provides no explicit name."

    Parameters
    ----------
    name_x      : list of strings
                  User provided exogenous variable names.
    name_q      : list of strings
                  User provided instrument variable names.

    Returns
    -------
    name_h      : list of strings

    """
    return name_x + name_q


def set_robust(robust):
    """Return generic name if user passes None to the robust parameter in a
    regression. Note: already verified that the name is valid in
    check_robust() if the user passed anything besides None to robust.

    Parameters
    ----------
    robust      : string or None
                  Object passed by the user to a regression class

    Returns
    -------
    robust      : string

    """
    if not robust:
        return "unadjusted"
    return robust


def set_name_w(name_w, w):
    """Return generic name if user passes None to the robust parameter in a
    regression. Note: already verified that the name is valid in
    check_robust() if the user passed anything besides None to robust.

    Parameters
    ----------
    name_w      : string
                  Name passed in by user. Default is None.
    w           : W object
                  pysal W object passed in by user

    Returns
    -------
    name_w      : string

    """
    if w != None:
        if name_w != None:
            return name_w
        else:
            return "unknown"
    return None


def set_name_multi(
    multireg,
    multi_set,
    name_multiID,
    y,
    x,
    name_y,
    name_x,
    name_ds,
    title,
    name_w,
    robust,
    endog=False,
    sp_lag=False,
):
    """Returns multiple regression objects with generic names

    Parameters
    ----------
    endog       : tuple
                  If the regression object contains endogenous variables, endog must have the
                  following parameters in the following order: (yend, q, name_yend, name_q)
    sp_lag       : tuple
                  If the regression object contains spatial lag, sp_lag must have the
                  following parameters in the following order: (w_lags, lag_q)

    """
    name_ds = set_name_ds(name_ds)
    name_y = set_name_y(name_y)
    name_x = set_name_x(name_x, x)
    name_multiID = set_name_ds(name_multiID)
    if endog or sp_lag:
        name_yend = set_name_yend(endog[2], endog[0])
        name_q = set_name_q(endog[3], endog[1])
    for r in multi_set:
        multireg[r].title = title + "%s" % r
        multireg[r].name_ds = name_ds
        multireg[r].robust = set_robust(robust)
        multireg[r].name_w = name_w
        multireg[r].name_y = "%s_%s" % (str(r), name_y)
        multireg[r].name_x = ["%s_%s" % (str(r), i) for i in name_x]
        multireg[r].name_multiID = name_multiID
        if endog or sp_lag:
            multireg[r].name_yend = ["%s_%s" % (str(r), i) for i in name_yend]
            multireg[r].name_q = ["%s_%s" % (str(r), i) for i in name_q]
            if sp_lag:
                multireg[r].name_yend.append(set_name_yend_sp(multireg[r].name_y))
                multireg[r].name_q.extend(
                    set_name_q_sp(
                        multireg[r].name_x, sp_lag[0], multireg[r].name_q, sp_lag[1]
                    )
                )
            multireg[r].name_z = multireg[r].name_x + multireg[r].name_yend
            multireg[r].name_h = multireg[r].name_x + multireg[r].name_q
    return multireg


def check_arrays(*arrays):
    """Check if the objects passed by a user to a regression class are
    correctly structured. If the user's data is correctly formed this function
    returns nothing, if not then an exception is raised. Note, this does not
    check for model setup, simply the shape and types of the objects.

    Parameters
    ----------
    *arrays : anything
              Objects passed by the user to a regression class; any type
              object can be passed and any number of objects can be passed

    Returns
    -------
    Returns : int
              number of observations

    Examples
    --------

    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_arrays
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')
    >>> # Extract CRIME column from the dbf file
    >>> y = np.array(db.by_col("CRIME"))
    >>> y = np.reshape(y, (49,1))
    >>> X = []
    >>> X.append(db.by_col("INC"))
    >>> X.append(db.by_col("HOVAL"))
    >>> X = np.array(X).T
    >>> n = check_arrays(y, X)
    >>> print(n)
    49

    """
    rows = []
    for i in arrays:
        if i is None:
            continue
        if not isinstance(i, (np.ndarray, csr_matrix)):
            raise Exception(
                "all input data must be either numpy arrays or sparse csr matrices"
            )
        shape = i.shape
        if len(shape) > 2:
            raise Exception("all input arrays must have two dimensions")
        if len(shape) == 1:
            shape = (shape[0], 1)
        if shape[0] < shape[1]:
            raise Exception("one or more input arrays have more columns than rows")
        if not spu.spisfinite(i):
            raise Exception("one or more input arrays have missing/NaN values")
        rows.append(shape[0])
    if len(set(rows)) > 1:
        raise Exception("arrays not all of same length")
    return rows[0]


def check_y(y, n):
    """Check if the y object passed by a user to a regression class is
    correctly structured. If the user's data is correctly formed this function
    returns nothing, if not then an exception is raised. Note, this does not
    check for model setup, simply the shape and types of the objects.

    Parameters
    ----------
    y       : anything
              Object passed by the user to a regression class; any type
              object can be passed

    n       : int
              number of observations

    Returns
    -------
    y       : anything
              Object passed by the user to a regression class

    Examples
    --------

    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_y
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')

    # Extract CRIME column from the dbf file

    >>> y = np.array(db.by_col("CRIME"))
    >>> y = np.reshape(y, (49,1))
    >>> y = check_y(y, 49)

    # should not raise an exception

    """
    if not isinstance(y, np.ndarray):
        print(y.__class__.__name__)
        raise Exception("y must be a numpy array")
    shape = y.shape
    if len(shape) > 2:
        raise Exception("all input arrays must have two dimensions")
    if len(shape) == 1:
        try:
            y = y.reshape(n, 1)
        except:
            raise Exception(
                "y must be a single column array matching the length of other arrays"
            )
    if y.shape != (n, 1):
        raise Exception(
            "y must be a single column array matching the length of other arrays"
        )
    return y


def check_weights(w, y, w_required=False, time=False):
    """Check if the w parameter passed by the user is a libpysal.W object and
    check that its dimensionality matches the y parameter.  Note that this
    check is not performed if w set to None.

    Parameters
    ----------
    w       : any python object
              Object passed by the user to a regression class; any type
              object can be passed
    y       : numpy array
              Any shape numpy array can be passed. Note: if y passed
              check_arrays, then it will be valid for this function
    w_required : boolean
                 True if a W matrix is required, False (default) if not.
    time    : boolean
              True if data contains a time dimension.
              False (default) if not.

    Returns
    -------
    Returns : nothing
              Nothing is returned

    Examples
    --------
    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_weights
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')
    >>> # Extract CRIME column from the dbf file
    >>> y = np.array(db.by_col("CRIME"))
    >>> y = np.reshape(y, (49,1))
    >>> X = []
    >>> X.append(db.by_col("INC"))
    >>> X.append(db.by_col("HOVAL"))
    >>> X = np.array(X).T
    >>> w = libpysal.io.open(libpysal.examples.get_path("columbus.gal"), 'r').read()
    >>> check_weights(w, y)

    # should not raise an exception

    """
    if w_required == True or w != None:
        if w == None:
            raise Exception("A weights matrix w must be provided to run this method.")
        if not isinstance(w, weights.W):
            from warnings import warn

            warn("w must be API-compatible pysal weights object")
        if w.n != y.shape[0] and time == False:
            raise Exception("y must have n rows, and w must be an nxn PySAL W object")
        diag = w.sparse.diagonal()
        # check to make sure all entries equal 0
        if diag.min() != 0:
            raise Exception("All entries on diagonal must equal 0.")
        if diag.max() != 0:
            raise Exception("All entries on diagonal must equal 0.")


def check_robust(robust, wk):
    """Check if the combination of robust and wk parameters passed by the user
    are valid. Note: this does not check if the W object is a valid adaptive
    kernel weights matrix needed for the HAC.

    Parameters
    ----------
    robust  : string or None
              Object passed by the user to a regression class
    w       : any python object
              Object passed by the user to a regression class; any type
              object can be passed

    Returns
    -------
    Returns : nothing
              Nothing is returned

    Examples
    --------
    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_robust
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')
    >>> # Extract CRIME column from the dbf file
    >>> y = np.array(db.by_col("CRIME"))
    >>> y = np.reshape(y, (49,1))
    >>> X = []
    >>> X.append(db.by_col("INC"))
    >>> X.append(db.by_col("HOVAL"))
    >>> X = np.array(X).T
    >>> wk = None
    >>> check_robust('White', wk)

    # should not raise an exception

    """
    if robust:
        if robust.lower() == "hac":
            if not isinstance(wk, weights.Kernel):
                raise Exception("HAC requires that wk be a Kernel Weights object")
            diag = wk.sparse.diagonal()
            # check to make sure all entries equal 1
            if diag.min() < 1.0:
                print(diag.min())
                raise Exception(
                    "All entries on diagonal of kernel weights matrix must equal 1."
                )
            if diag.max() > 1.0:
                print(diag.max())
                raise Exception(
                    "All entries on diagonal of kernel weights matrix must equal 1."
                )
            # ensure off-diagonal entries are in the set of real numbers [0,1)
            wegt = wk.weights
            for i in wk.id_order:
                vals = wegt[i]
                vmin = min(vals)
                vmax = max(vals)
                if vmin < 0.0:
                    raise Exception(
                        "Off-diagonal entries must be greater than or equal to 0."
                    )
                if vmax > 1.0:
                    # NOTE: we are not checking for the case of exactly 1.0 ###
                    raise Exception("Off-diagonal entries must be less than 1.")
        elif robust.lower() == "white" or robust.lower() == "ogmm":
            if wk:
                raise Exception("White requires that wk be set to None")
        else:
            raise Exception(
                "invalid value passed to robust, see docs for valid options"
            )


def check_spat_diag(spat_diag, w):
    """Check if there is a w parameter passed by the user if the user also
    requests spatial diagnostics.

    Parameters
    ----------
    spat_diag   : boolean
                  Value passed by a used to a regression class
    w           : any python object
                  Object passed by the user to a regression class; any type
                  object can be passed

    Returns
    -------
    Returns : nothing
              Nothing is returned

    Examples
    --------
    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_spat_diag
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')
    >>> # Extract CRIME column from the dbf file
    >>> y = np.array(db.by_col("CRIME"))
    >>> y = np.reshape(y, (49,1))
    >>> X = []
    >>> X.append(db.by_col("INC"))
    >>> X.append(db.by_col("HOVAL"))
    >>> X = np.array(X).T
    >>> w = libpysal.io.open(libpysal.examples.get_path("columbus.gal"), 'r').read()
    >>> check_spat_diag(True, w)

    # should not raise an exception

    """
    if spat_diag:
        if not isinstance(w, weights.W):
            raise Exception("w must be a libpysal.W object to run spatial diagnostics")


def check_regimes(reg_set, N=None, K=None):
    """Check if there are at least two regimes

    Parameters
    ----------
    reg_set     : list
                  List of the regimes IDs

    Returns
    -------
    Returns : nothing
              Nothing is returned

    """
    if len(reg_set) < 2:
        raise Exception(
            "At least 2 regimes are needed to run regimes methods. Please check your regimes variable."
        )
    if 1.0 * N / len(reg_set) < K + 1:
        raise Exception(
            "There aren't enough observations for the given number of regimes and variables. Please check your regimes variable."
        )


def check_constant(x, name_x=None, just_rem=False):
    """Check if the X matrix contains a constant. If it does, drop the constant and replace by a vector of ones.

    Parameters
    ----------
    x           : array
                  Value passed by a used to a regression class
    name_x      : list of strings
                  Names of independent variables
    just_rem    : boolean
                  If False (default), remove all constants and add a vector of ones
                  If True, just remove all constants
    Returns
    -------
    x_constant : array
                 Matrix with independent variables plus constant
    name_x     : list of strings
                 Names of independent variables (updated if any variable droped)
    Examples
    --------
    >>> import numpy as np
    >>> import libpysal
    >>> from spreg import check_constant
    >>> db = libpysal.io.open(libpysal.examples.get_path('columbus.dbf'),'r')
    >>> X = []
    >>> X.append(db.by_col("INC"))
    >>> X.append(db.by_col("HOVAL"))
    >>> X = np.array(X).T
    >>> x_constant,name_x,warn = check_constant(X)
    >>> x_constant.shape
    (49, 3)

    """
    x_constant = COPY.copy(x)
    keep_x = COPY.copy(name_x)
    warn = None
    if isinstance(x_constant, np.ndarray):
        diffs = np.ptp(x_constant, axis=0)
        if sum(diffs == 0) > 0:
            x_constant = np.delete(x_constant, np.nonzero(diffs == 0), 1)
    else:
        diffs = (x_constant.max(axis=0).toarray() - x_constant.min(axis=0).toarray())[0]
        if sum(diffs == 0) > 0:
            x_constant = x_constant[:, np.nonzero(diffs > 0)[0]]

    if sum(diffs == 0) > 0:
        if keep_x:
            rem_x = [keep_x[i] for i in np.nonzero(diffs == 0)[0]]
            warn = "Variable(s) " + str(rem_x) + " removed for being constant."
            keep_x[:] = [keep_x[i] for i in np.nonzero(diffs > 0)[0]]
        else:
            if sum(diffs == 0) == 1:
                warn = "One variable has been removed for being constant."
            else:
                warn = (
                    str(sum(diffs == 0))
                    + " variables have been removed for being constant."
                )
    if not just_rem:
        return spu.sphstack(np.ones((x_constant.shape[0], 1)), x_constant), keep_x, warn
    else:
        return x_constant, keep_x, warn


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
