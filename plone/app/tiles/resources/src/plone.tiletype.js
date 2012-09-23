// Plone TileTypes
// ===============
//
// Author: Rok Garbas
// Contact: rok@garbas.si
// Version: 1.0
// Depends:
//    ++resource++plone.app.jquery.js
//
// Description: 
//
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
$.plone.tiletype = $.plone.tiletype || {};


// # Helper utility
$.plone.tiletype.getTileNameByElement = function(el) {
  return (/@@(.*)\//).exec(el.attr('data-tile'))[1];
};


// # Base Class
$.plone.tiletype.Base = {
  init: function(name) {
    var self = this;
    self.name = name;
    self.id = name.replace(/\./g, '-');
  },
  createProxy: function() {
    return $('<div/>').css({
      'opacity': 0.75,
      'z-index': 1000,
      'position': 'absolute',
      'border': '1px solid #89B',
      'background': '#BCE',
      'height': '58px',
      'width': '258px'
      });
  },
  createPreview: function() {
    return $('<div/>').css({
      'cursor': 'move',
      'width': '100%',
      'height': '50px',
      'background': '#BCE',
      'border': '1px solid #89B',
      'border-radius': '3px'
      });
  },
  styleButtons: function(buttons) {
    buttons.css("cssText", "color: #333333 !important;");
    buttons.css({
      'cursor': 'pointer',
      'text-align': 'center',
      'text-shadow': '0 1px 1px rgba(255, 255, 255, 0.75)',
      'font-size': '11px',
      'line-height': '14px',
      'vertical-align': 'middle',
      'padding': '2px 6px',
      'margin-bottom': '0',

      'background-color': '#f5f5f5',
      'background-image': 'linear-gradient(top, #ffffff, #e6e6e6)',
      'background-repeat': 'repeat-x',
      '-webkit-box-shadow': 'inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05)',
      '-moz-box-shadow': 'inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05)',
      'box-shadow': 'inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 1px 2px rgba(0, 0, 0, 0.05)',

      'border': '1px solid #cccccc',
      'border-color': '#e6e6e6 #e6e6e6 #bfbfbf',
      'border-bottom-color': '#b3b3b3',
      '-webkit-border-radius': '4px',
      '-moz-border-radius': '4px',
      'border-radius': '4px'
    });
  },
  styleActions: function(actions) {
    var self = this;
    self.styleButtons($('> li > a', actions));
    $('> li', actions).css('display', 'inline');
    actions.css({
      'z-index': '700',
      'position': 'absolute',
      'top': '0.3em',
      'right': '0.5em',
      'list-style': 'none',
      'margin': '0',
      'padding': '0'
    });
  },
  getActions: function() {
    var self = this,
        actions = $('#plone-tiletype-' + self.id +
            ' .plone-tiletype-actions').clone();
    self.styleActions(actions);
    return actions;
  }
};


// # TileType Registry
function createTileType(name, tiletype, base) {
  var TileType = function() {
    this.__super = base || $.plone.tiletype.Base;
    this.init(name);
  };
  TileType.prototype = $.extend(
    base || $.plone.tiletype.Base,
    tiletype || {});
  return TileType;
}
$.plone.tiletype.__all = {};
$.plone.tiletype.get = function(name) {
  if ($.plone.tiletype.__all[name] === undefined) {
    return createTileType(name);
  } else {
    return $.plone.tiletype.__all[name];
  }
};
$.plone.tiletype.register = function(name, tiletype, base) {
  $.plone.tiletype.__all[name] = createTileType(name, tiletype, base);
  return $.plone.tiletype.__all[name];
};


}(jQuery));
