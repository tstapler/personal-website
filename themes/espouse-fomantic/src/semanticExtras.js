import 'jquery'
import '../dist/components/label.css'
import '../dist/components/table.css'

import '../dist/components/sticky.css'
import '../dist/components/sticky.js'

import '../dist/components/dimmer.css'
import '../dist/components/dimmer.js'

import '../dist/components/sidebar.css'
import '../dist/components/sidebar.js'

import '../dist/components/transition.css'
import '../dist/components/transition.js'

import '../dist/components/modal.css'
import '../dist/components/modal.js'



// fix main menu to page on passing
$('.main.menu').sticky({
  context: '#footer'
})

$('#menuButton').click(function(){
  $('.ui.labeled.icon.sidebar')
    .sidebar('toggle')
})

function uuid() {
var result='';
for(var i=0; i<32; i++)
result += Math.floor(Math.random()*16).toString(16).toUpperCase
();
return result
}

// Lightbox for photos using Semantic UI
// Should work for the image shortcode
$('.post-image').click(function() {
  var image = $(this)
    .children('img')
    .attr('src')
  var id = uuid()
  $('body').append(
    `<div id=${id} class="ui modal">
        <img class="ui centered image" src="${image}"/>
    </div>`
  )

  $(`#${id}`).modal({
    onHidden: () => $(`#${id}`).remove()
  })

  $(`#${id}`).modal('show')
})
