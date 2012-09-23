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

  // TODO: move this to plone.tile.js
  // ## initialize tile's editform with ploneOverlay
  //self.overlay = new $.plone.overlay.Overlay({
  //  url: el.attr('data-tile') || self.tiletype.createAddTileUrl(),
  //  form: 'form#edit_tile,form#add_tile',
  //  save: function(response) {
  //    self.overlay.hide();
  //  }
  //});


      // TODO: move this to plone.tile.js
      // TODO:  double click should also trigger click on editButton
      //self.el_view.off('dblclick').on('dblclick', function(e) {
      //    self.tiletype.editButton.trigger('click');
      //  });

    // TODO: move this to plone.tile.js
    // ## for tiles that are already in grid, show edit button on hover
    //if (self.el.attr('data-tile') !== undefined) {

// # Tile Class
$.plone.tile.Tile = function(el, options) { this.init(el, options); };
$.plone.tile.Tile.prototype = {
  init: function(el, options) {
    var self = this;

    self.el = el;
    self.options = $.extend(true, {
      overlay: {
        form: 'form#edit_tile,form#add_tile',
        save: function(response) {
          var overlay = this;
          overlay.destroy();
          overlay._init(overlay.options);
          self.el.html(response.html());
          // save deco layout as well
          var decoToolbar = $($.plone.deco.defaults.toolbar).decoToolbar();
          decoToolbar._editformDontHideDecoToolbar = true;
          $($.plone.deco.defaults.form_save_btn, decoToolbar._editform).click();
        }
      }
    }, options || {});
    self.name = $.plone.tiletype.getTileNameByElement(el);
    self.type = new ($.plone.tiletype.get(self.name))();
    self.actions = self.type.getActions();
    self.wrapper = self.options.wrapper;

  },
  show: function() {
    var self = this;

    // create tile wrapper if not passing in options
    if (self.wrapper === undefined) {
      self.wrapper = $('<div/>').addClass('plone-tile');
      self.el.wrap(self.wrapper);
    }

    // make sure wrapper has relative position
    self.wrapper.css('position', 'relative');

    // add actions to wrapper
    self.wrapper.append(self.actions);

    // show actions on hover
    $('li > a', self.actions).off('hover').on('hover', function(e) {
      if (self.actions.is(":visible")) {
        self.actions.show();
      } else {
        self.actions.hide();
      }
    });
    self.wrapper.off('hover').on('hover', function(e) {
      if (self.actions.is(":visible")) {
        self.actions.hide();
      } else {
        self.actions.show();
      }
    });

    // edit action in overlay
    $('li > a.plone-tiletype-action-edit', self.actions)
      .attr('href', $('base', window.parent.document).attr('href') +
          self.el.attr('data-tile').replace(/@@(.*)\//, '@@edit-tile/' + self.type.name + '/'))
      .ploneOverlay(self.options.overlay);

    // remove action
    $('li > a.plone-tiletype-action-remove', self.actions)
      .attr('href', $('base', window.parent.document).attr('href') +
          self.el.attr('data-tile').replace(/@@(.*)\//, '@@delete-tile' + '/'))
      .on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var el = $(this);
        el.ajaxSubmit({
          url: el.attr('href'),
          success: function(response) {
            el.parents('.deco-tile').remove();
            // save deco layout as well
            var decoToolbar = $($.plone.deco.defaults.toolbar).decoToolbar();
            decoToolbar._editformDontHideDecoToolbar = true;
            $($.plone.deco.defaults.form_save_btn, decoToolbar._editform).click();
          }
      });
    });


  },
  hide: function() {
    var self = this;

    // remove wrapper if not defined in options
    if (self.options.wrapper === undefined) {
      self.el.unwrap();
    }

    // detach actions from dom
    self.actions.remove();
  }
};


// # jQuery integration
$.fn.ploneTile = function(options) {
  var el = $(this),
      data = el.data('plone-tile');
  if (data === undefined) {
    data = new $.plone.tile.Tile(el, options);
    el.data('plone-tile', data);
  }
  return data;
};

}(jQuery));
