<template>
  <div class="sidebar">
    <multiselect v-if="tracks.length < 4" v-model="value" :options="options" :multiple="true" :close-on-select="false" :clear-on-select="false" :hide-selected="true" placeholder="Pick some" label="name" track-by="name"></multiselect>
    <draggable v-model="locTrack" @end="drag">
    <div v-for="(track, index) in locTrack" :key="index">
      <p style="font-size: 12px;">
      <span v-on:click="changePlot(index)">{{ track.type }} </span>
      <span v-on:click="removeTrack(index)">[X]</span>
      </p>
    </div>
    </draggable>
    <div v-if="tracks.length < 4" :key="4">
      <span v-on:click="addTrack">[+]</span>
    </div>
    <form id="search">
      <input name="query" placeholder="search table" v-model="searchQuery">
    </form>
    <site-table
         :data="gridData"
         :columns="gridColumns"
         :filter-key="searchQuery"
         v-on:updateSelected="updateSelected"></site-table>
  </div>
</template>

<script>
  import SiteTable from './site-table/site-table.vue'

  import _ from 'lodash'
  const zlib = require('zlib')

  import draggable from 'vuedraggable'
  import Multiselect from 'vue-multiselect'

  export default {
    name: 'sidebar',
    props: [
      'tracks',
      'selected'
    ],
    data () {
      return {
        locTrack: this.tracks,
        value: [{name: 'gg'}],
        options: [
          {name: 'gg'},
          {name: 'gn'},
          {name: 'gl'},
          {name: 'gj'},
          {name: 'll'},
          {name: 'ln'},
          {name: 'lj'},
          {name: 'jn'},
          {name: 'jj'}
        ],
        searchQuery: '',
        gridColumns: ['Location', 'Gene', 'Probability'],
        gridData: []
      }
    },
    methods: {
      updateSelected (s) {
        this.$emit('updateSelected', s)
      },
      update: function () {

      },
      drag () {
        // console.log(this.locTrack, 'dropped')
        this.$emit('reorder', this.locTrack)
      },
      addTrack: function () {
        // var t = _.sampleSize(['gg', 'gl', 'gj', 'jl'], _.random(1, 4))
        // this.locTrack.push({type: t})
        this.$emit('addTrack', _.map(this.value, 'name'))
        this.value = []
      },
      removeTrack: function (index) {
        // console.log(_.join(_.map(this.tracks, t => t.type)))
        // _.pullAt(this.tracks, [index])
        this.tracks.splice(index, 1)
        // this.
        // console.log(_.join(_.map(this.tracks, t => t.type)))
        this.$emit('removeTrack', index)
      },
      changePlot: function (index) {
        // this.log('change')
      }
    },
    components: {
      draggable,
      Multiselect,
      SiteTable
    },
    created () {
      var oReq = new XMLHttpRequest()

      oReq.open('get', './static/ovarian/918/918_TS/table_info.json.gz.txt', true)
      // oReq.open('get', '/static/Hu_Output_Ver7.txt', true)
      oReq.onreadystatechange = (aEvt) => {
        if (oReq.readyState === XMLHttpRequest.DONE) {
          const buffer = Buffer.from(oReq.responseText, 'base64')
          zlib.unzip(buffer, (err, buffer) => {
            if (!err) {
              var table = JSON.parse(buffer.toString())
              table.Heading = _.map(table.Heading, i => i.split(' ')[0])
              table.Heading[2] = 'P'
              this.gridColumns = table.Heading
              table = _.map(table.Data, s => _.zipObject(table.Heading, [[s[0], 'black'], s[1], [s[2], 'blue']]))
              // console.log(table)
              this.gridData = table
              this.$emit('updateSelected', table[0])
            } else {
              console.log(err)
              // handle error
            }
          })
          // var temp = oReq.responseText.replace(/\n$/, '').split('\n')
          // var keys = temp.shift().split('\t')
          // var o = _.map(temp, (t) => _.zipObject(keys, _.map(t.replace(/'/g, '').split('\t'))))

          // console.log(o)
        }
      }
      oReq.onprogress = function (event) {
        event.loaded
        event.total
        console.log(event.loaded / event.total)
      }
      oReq.send()
    }
    // data: function () {
      // return {
        // tracks: [1]
      // }
    // }
  }
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style>
.sidebar {
  background: #f5f5f5;
  /* background: #455A64; */
  overflow-y: hidden;
  height: 100%;
}
</style>
