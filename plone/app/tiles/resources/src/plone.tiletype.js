// Plone TileTypes
// ===============
//
// Author: Rok Garbas
// Contact: rok@garbas.si
// Version: 1.0
// Depends:
//    ++resource++plone.app.jquery.js
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
  regexp:true, undef:true, strict:true, trailing:true, browser:true */
/*global jQuery:false */


(function ($) {
"use strict";

// # Namespace
$.plone = $.plone || {};
$.plone.tiletype = $.plone.tiletype || {};


// # TileType Registry
$.plone.tiletype.__tiletypesByName = {};
$.plone.tiletype.register = function(name, tiletype) {
  $.plone.tiletype.__tiletypesByName[name] = tiletype;
};


// # Base Class
$.plone.tiletype.Base = {
  init: function(tile) {
    this.tile = tile;
    this.name = (/@@(.*)\//).exec(tile.attr('data-tile'))[1];
  },
  getActions: function() {
    // TODO: must be cloned from deco toolbar
  }
};

//
// # TileType Factory
$.plone.tiletype.TileType = function(tiletype, base) {
  var TileType = function(tile) {
    this.__super = base || $.plone.tiletype.Base;
    this.init(tile);
  };
  TileType.prototype = $.extend(
    base || $.plone.tiletype.Base,
    tiletype || {});
  return TileType;
};


}(jQuery));
