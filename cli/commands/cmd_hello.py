import subprocess
import click

@click.command()
@click.option('--name', default=True, help='What Name ?')


def cli(name):
	"""
	Run hello test
	:param name: print hello name provided
	:param path: hello path
	:return: subprocess call result
	"""
	print 'hello ' + str(name)

	cmd = 'hello {0}'.format(name)
	return subprocess.call(cmd, shell=True)	

