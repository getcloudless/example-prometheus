# Prometheus Example

This is an example of creating a simple single node Prometheus setup. Note that
this blueprint references an image created by the base image scripts at
[https://github.com/getcloudless/example-base-image](https://github.com/getcloudless/example-base-image),
so this will fail unless you run that first.

## Installation

You can clone this repo, and then install Cloudless and the other dependencies
using [pipenv](https://pipenv.readthedocs.io/en/latest/):

```shell
$ git clone https://github.com/getcloudless/example-prometheus.git
$ cd example-prometheus
$ pipenv install
$ pipenv shell
$ which cldls
```

## Usage

The file at `blueprint.yml` can be used in any service command:

```
cldls service create blueprint.yml
```

You can run the service's regression tests with:

```
cldls service-test run service_test_configuration.yml
```

Note that these are completely independent of what provider you're using,
assuming you've already built the [Base
Image](https://github.com/getcloudless/example-base-image).

## Workflow

The main value of the test framework is that it is focused on the workflow of
actually developing a service.  For example, if you want to deploy a service
(and all its dependencies) that you can work on without running the full test,
you can run:

```
cldls service-test deploy service_test_configuration.yml
```

This command saves the SSH keys locally and will display the SSH command that
you need to run to log into the instance.

Now, say you want to actually check that the service is behaving as expected:

```
cldls service-test check service_test_configuration.yml
```

You can run this as many times as you want until it's working, as you are logged
in.  Finally, clean everything up with:

```
cldls service-test cleanup service_test_configuration.yml
```

You're done!  The run step will run all these steps in order.
