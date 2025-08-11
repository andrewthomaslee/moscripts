import moscripts


def test_hello(capsys):
    moscripts.main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from development-scripts!\n"
    assert captured.err == ""