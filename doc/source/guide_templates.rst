Guide for Templates
===================

Overview
--------
There is a marketplace for shareable App policies. In the UI sidebar, there is a section labeled “Templates”.
Araali has started publishing public templates for well-known apps starting with Araali apps. Private templates can be created
to auto-approve based on pattern matching, and user contribution to the marketplace will be possible in the future
(today the public policies are Araali-controlled).

These templates are not acted upon by default; they are only intended for people who want to cruise control by putting
the approval process on auto-pilot (this is based on published and community-reviewed App patterns). These templates can
be stopped with the click of a button. It is also possible to do all of this with APIs.

`Enabling the “araalifw-kube” template <https://vimeo.com/573261476>`_ will auto-approve all Araali links and
suppress any alerts coming from Araali's app (Daemonset/Operator).

Please note that the public template for Araali is still being tested internally. It should be safe for use:
it just may not be comprehensive or complete yet.


Guide for Araali SW Template
----------------------------

Araali baselines your application communication and presents them as
identity-based links that can then be accepted as policy. This means no
handwriting policies, everything is automatically discovered.

One of the easier ways to accept policies is through UI Templates. Araali has
published a template for its own software in the "Public" folder that can be
used to auto-accept Araali’s own policies.


When to use Templates
---------------------
Templates are particularly useful when:

- You are an app owner and want to publish your app's profile into a
  marketplace that anyone can use and benefit from. Ideally you want to publish
  to the marketplace whenever there are app changes that necessitate a refresh.

- You have common patterns that apply across app/service lenses. You can define
  patterns in template once, and apply it across lenses to do the
  greening/policy-accepting based on pattern matching.

- You want to edit/customize a node (say use .* as regex for the pid in
  snapd binaray path). You can alternatively select links and edit them
  individually (repeating the editing to put the .* on a per link basis). The
  benefit of using template is that you can edit a node once, and add new links
  to the template. The node editing is automatically inherited as you add a
  link to an existing template. This is only available via api currently. We
  are trying to get it to UI sometime soon.

Applying Araali Template in UI
------------------------------

In the Araali UI, go to the Public Template and click on the download icon next to "araalifw-kube" template.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/template-araali-public.png
 :width: 600
 :alt: Public Araali Templates

This will open a window. The template is very flexible and allows you to further customize using regex. We recommend that you use the template as is. You can change the name of the template, check the box "search and use continuously" and then save the template.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/template-araali-public-use.png
 :width: 600
 :alt: Saving Public Template as Private

This will instantiate a local copy of the template in your “Private” folder. If you go to the folder you can see the template running. If you want to stop the template, you can click on the orange stop button.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/template-is-private-use-button.png
 :width: 600
 :alt: Saving Public Template as Private

Now if you go back to your kube-system app and refresh the page, you will see all the links from araali-fw pod green.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araali-fw-container-green.png
 :width: 600
 :alt: Saving Public Template as Private

Programmatic Manipulation
-------------------------

Get
***

Get all templates. It is possible to optionally filter for public templates or access a specific template.

.. tabs::
   .. code-tab:: sh Command Line

        # Get all templates
        ./araalictl api -list-templates

        # Get only public templates
        ./araalictl api -list-templates -public

        # Specify a template
        ./araalictl api -list-templates -template template_name

   .. code-tab:: py

        # Without params it will get all templates
        # Use public=True explictly to get the subset that is public
        # Optionally specify template name as string
        api.Templates(public=False, template=None)

Rename
******

Rename an existing template

.. tabs::
   .. code-tab:: sh Command Line

        # Copy the output of the following
        # Use existing template name
        ./araalictl api -list-templates -template old_t_name

        # "i" to insert at cursor, "a" for after cursor, and "o" for line above cursor
        vi edit_template.txt
        # Paste previously-copied output
        # Change existing name to desired name
        # Esc to exit edit mode in vi
        # “:wq” to quit once in control mode
        cat edit_template.txt | ./araalictl api -update-template -template old_t_name

   .. code-tab:: py

        .rename(new_name)

Save
****

Save a link as a template

.. tabs::
   .. code-tab:: sh Command Line

        # Fetch links for desired zone-app
        ./araalictl api -fetch-links -zone z_name -app a_name
        # Copy desired link(s)
        # "i" to insert at cursor, "a" for after cursor, and "o" for line above cursor
        vi za_template.txt
        # Paste previously-copied link(s)
        # Esc to exit edit mode in vi
        # “:wq” to quit once in control mode

        # Add "-use-template-link" to Search and Use Continuously
        #
        cat za_template.txt | ./araalictl -save-link-template

   .. code-tab:: py

        # App to template
        app.template()
