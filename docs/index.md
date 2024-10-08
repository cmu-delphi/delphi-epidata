---
title: Epidata API Intro
has_children: true
nav_order: 1
---

# The Epidata API

Delphi's Epidata API provides real-time access to epidemiological surveillance data.
It is built and maintained by the Carnegie Mellon University [Delphi research
group](https://delphi.cmu.edu/). The Epidata API includes:

* The [main endpoint (COVIDcast)](api/covidcast.md), providing daily updates about current COVID-19 and influenza activity across the United States.
* A [variety of other endpoints](api/README.md), providing primarily historical data about various diseases including COVID-19, influenza, dengue fever, and norovirus in several countries.

A [full-featured R client](api/client_libraries.md) is available for quick access to all data. While we continue developing a full-featured Python client, the [legacy Python client](api/client_libraries.md#python) remains available. The main endpoint can also be accessed with a [dedicated COVIDcast client](api/covidcast_clients.md).

Anyone may access the Epidata API anonymously without providing any personal
data. Anonymous API access is currently rate-limited and restricted to public
datasets with a maximum of two of the requested parameters having multiple
selections (signals, dates, versions, regions, etc).

To request access with no rate limit and unlimited multiple
selections, you can [request a registered API key](https://api.delphi.cmu.edu/epidata/admin/registration_form).
For policy and usage details, consult the [Epidata API keys documentation](api/api_keys.md).

If you regularly or frequently use our system, please consider using an API key
even if your usage falls within the anonymous usage limits. API key usage helps
us understand who and how others are using our Delphi Epidata API, which may in
turn inform our future research, data partnerships, and funding.

For more information about how we use the data you provide us through your
registration and API request activity, see our
[Privacy Statement](api/privacy_statement.md). At any time, you may submit a
[Deletion Request](https://api.delphi.cmu.edu/epidata/admin/removal_request) to
have us deactivate your key and destroy all information associating that key
with your identity.

The Delphi group is extremely grateful to Pedrito Maynard-Zhang for all his
help with the Epidata API [documentation](api/README.md).

Developers interested in modifying or extending this project are directed to
the [Epidata API Development Guide](epidata_development.md).
