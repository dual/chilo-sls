def mock_before_all(request, response, requirements):
    mock_before_all.has_been_called = True


def mock_after_all(request, response, requirements):
    mock_after_all.has_been_called = True


def mock_with_auth(request, response, requirements):
    mock_with_auth.has_been_called = True
def mock_when_auth_required(request, response, requirements):
    mock_when_auth_required.has_been_called = True


def mock_on_error(request, response, error):
    mock_on_error.has_been_called = True


def mock_on_error_exception(request, response, error):
    mock_on_error_exception.has_been_called = True
    raise Exception('something went wrong with middleware')


def mock_on_timeout(request, response, error):
    mock_on_timeout.has_been_called = True


def mock_on_startup():
    mock_on_startup.has_been_called = True


def mock_on_shutdown():
    mock_on_shutdown.has_been_called = True
