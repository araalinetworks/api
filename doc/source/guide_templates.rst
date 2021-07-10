Guide for Araali SW Template
============================

Araali baselines your application communication and presents them as identity-based links that can then be accepted as policy. This means no handwriting policies, everything is automatically discovered.

One of the easier ways to accept policies is through UI Templates. Araali has published a template for its own software in the "Public" folder that can be used to auto-accept Araali’s own policies.


Applying Araali Template in UI
******************************

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
