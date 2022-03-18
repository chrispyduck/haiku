---
layout: page
---

<ul class="haiku-feed">
{% for haiku_hash in site.data.haiku %}
{% assign haiku = haiku_hash[1][0] %}
  <li class="haiku">
    <p class="text">
    {% for line in haiku.text %}
      {{ line }}<br/>
    {% endfor %}
    </p>
    <div class="signature">
      <span class="author">{{ haiku.author }}</span>
      <span class="date">{{ haiku.timestamp | date_to_string }}</span>
    </div>
  </li>
{% endfor %}
</ul>