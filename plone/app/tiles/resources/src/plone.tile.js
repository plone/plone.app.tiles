// Plone Tiles
// ===========
//
// Author: Rok Garbas
// Contact: rok@garbas.si
// Version: 1.0
// Depends:
//    ++resource++plone.app.jquery.js
//    ++resource++plone.app.toolbar/src/plone.overlay.js
// Description: 
// License:
//
// Copyright (C) 2012 Plone Foundation
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 of the License.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
// more details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc., 51
// Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//

/*jshint bitwise:true, curly:true, eqeqeq:true, immed:true, latedef:true,
  newcap:true, noarg:true, noempty:true, nonew:true, plusplus:true,
  undef:true, strict:true, trailing:true, browser:true */
/*global jQuery:false */


(function ($) {
"use strict";

// # Namespace
$.plone = $.plone || {};
$.plone.tile = $.plone.tile || {};


// # Tile Class
$.plone.tile.Tile = function(el, options) { this.init(el, options); };
$.plone.tile.Tile.prototype = {
  init: function(el, options) {
    var self = this;

    self.el = el;
    self.options = options;
    self.tiletype = $.plone.tile.types[self.getTileTypeName(el)];
    self.actions = self.tiletype.getActions();
    self.wrapper = options.wrapper;

    // create tile wrapper if not passing in options
    if (self.wrapper !== undefined) {
      self.wrapper = $('<div/>').addClass('plone-tile');
      el.wrap(self.wrapper);
    }

    // make sure wrapper has relative position
    self.wrapper.css('position', 'relative');

    // add actions to wrapper
    self.wrapper.append(self.actions);

    // contextualize url's of actions
    $('li > a.plone.tiletype-action', self.actions).each(function() {
      $(this).attr('href', el.attr('data-tile').replace(/@@(.*)\//,
          $(this).attr('href') + '/' + self.tiletype.name + '/'));
    });

    // save action
    var data = $('li > a.plone-tiletype-action-edit', self.actions)
        .ploneOverlay(options.overlay);

    // TODO: remove action
    // TODO: other actions

  },
  getTileTypeName: function(el) {
    return (/@@(.*)\//).exec(el.attr('data-tile'))[1];
  }
};


// # jQuery integration
$.fn.ploneTile = function(options) {
  var el = $(this),
      data = el.data('plone-tile');
  if (data === undefined) {
    data = new $.plone.tiles.Tile(el, options);
    el.data('plone-tile', data);
  }
  return data;
};

}(jQuery));
