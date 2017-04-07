<template>
  <section>
    <nav class="nav">
      <div class="nav-left">
        <h1 class="title nav-item">
        TranspoScope
        </h1>
      </div>

      <div class="nav-center">
        <a class="nav-item">
          <span class="icon">
            <i class="fa fa-github"></i>
          </span>
        </a>
        <a class="nav-item">
          <span class="icon">
            <i class="fa fa-twitter"></i>
          </span>
        </a>
      </div>

      <!-- This "nav-toggle" hamburger menu is only visible on mobile -->
      <!-- You need JavaScript to toggle the "is-active" class on "nav-menu" -->
      <span class="nav-toggle">
        <span></span>
        <span></span>
        <span></span>
      </span>

      <!-- This "nav-menu" is hidden on mobile -->
      <!-- Add the modifier "is-active" to display it on mobile -->
      <div class="nav-right nav-menu">
        <a class="nav-item">
          Home
        </a>
        <a class="nav-item">
          Documentation
        </a>
        <a class="nav-item">
          Blog
        </a>

        <span class="nav-item">
          <a class="button" >
            <span class="icon">
              <i class="fa fa-twitter"></i>
            </span>
            <span>Tweet</span>
          </a>
          <a class="button is-primary">
            <span class="icon">
              <i class="fa fa-download"></i>
            </span>
            <span>Download</span>
          </a>
        </span>
      </div>
    </nav>
    <div class="content full-height-with-nav">
      <div class="columns is-gapless full-height">
        <div class="column is-10 full-height">
          <div class='track-space full-height overflow-hidden'>
            <div v-for="t in tracks" :style="{background: 'red', height: trackheight + '%'}">
              <chart :initialData="dataframe" :catagories="t.type"></chart>
            </div>
          </div>
        </div>
        <div class="column is-2 full-height">
          <sidebar :tracks="tracks" v-on:removeTrack="removeTrack" v-on:updateSelected="updateSelected" v-on:addTrack="createTrack" v-on:reorder="reorder"></sidebar>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import chart from './chart.vue'
import sidebar from './sidebar.vue'
import _ from 'lodash'
const zlib = require('zlib')
export default {
  name: 'hello',
  data: function () {
    return {
      tracks: [{col: 'red', type: ['gg', 'gn', 'gl', 'gj', 'll', 'ln', 'lj', 'jj', 'jn']}],
      trackheight: 100,
      dataframe: {
        'gg': [0, 0, 0, 0, 0],
        'gn': [0, 0, 0, 0, 0],
        'gl': [0, 0, 0, 0, 0],
        'gj': [0, 0, 0, 0, 0],
        'll': [0, 0, 0, 0, 0],
        'ln': [0, 0, 0, 0, 0],
        'lj': [0, 0, 0, 0, 0],
        'jn': [0, 0, 0, 0, 0],
        'jj': [0, 0, 0, 0, 0]
      }
    }
  },
  methods: {
    updateSelected (s) {
      var oReq = new XMLHttpRequest()

      oReq.open('get', './static/ovarian/918/918_TS/' + s.ID[0] + '.json.gz.txt', true)
      // oReq.open('get', '/static/Hu_Output_Ver7.txt', true)
      oReq.onreadystatechange = (aEvt) => {
        if (oReq.readyState === XMLHttpRequest.DONE) {
          const buffer = Buffer.from(oReq.responseText, 'base64')
          zlib.unzip(buffer, (err, buffer) => {
            if (!err) {
              var data = JSON.parse(buffer.toString())
              console.log(data)
              // table.Heading = _.map(table.Heading, i => i.split(' ')[0])
              // table.Heading[2] = 'P'
              // this.gridColumns = table.Heading
              // table = _.map(table.Data, s => _.zipObject(table.Heading, [[s[0], 'black'], s[1], [s[2], 'blue']]))
              // // console.log(table)
              // this.gridData = table
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
    },
    createTrack: function (v) {
      // console.log(v)
      // console.log(this.trackheight)
      if (this.tracks.length < 4) {
        this.tracks.push({
          type: v
        })
        this.update()
      }
      // this.$refs.forEach(function (d) {
        // console.log(d)
      // })
    },
    removeTrack: function () {
      this.update()
    },
    reorder (t) {
      this.tracks = t
      this.update()
    },
    update: function () {
      // console.log('updating')
      this.trackheight = 100 / this.tracks.length
      console.log('th', this.trackheight)
      this.$nextTick(function () {
        _.forEach(this.$children, (c) => c.update())
        // for (var i = 0; i < this.tracks.length - 1; i++) {
          // console.log(i, this.$children[i])
          // this.$children[i].$data.sites.push(Math.random() * 100)
          // this.$children[i].$data.tracks.push(this.tracks.length)
          // this.$children[i].update()
        // }
      })
    }
  },
  components: {
    chart,
    sidebar
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.hero-body {
  background: white;
}

.full-height {
  height: 100%;
}

.full-height-with-nav {
  height: calc(100% - 52px);

}
.overflow-hidden {
  overflow-y: hidden;
}

section {
  height: 100%;
}

.nav {
  background: #455A64;
}
</style>
