<template>
  <div class="svg-holder"></div>
</template>

<script>
  import * as d3 from 'd3'
  import _ from 'lodash'
  const margin = {top: 20, right: 10, bottom: 20, left: 20}
  export default {
    name: 'chart',
    props: ['initialData', 'catagories'],
    data: function () {
      return {
      }
    },
    mounted () {
      window.addEventListener('resize', this.handleWindowResize)
      this.svg = d3.select(this.$el)
        .append('svg')
        .attr('width', this.$el.clientWidth + margin.left + margin.right)
        .attr('height', this.$el.clientHeight + margin.top + margin.bottom)
      this.chartWrapper = this.svg.append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
      this.chartWrapper.append('g')
          .attr('class', 'y axis')
      this.drawSVG()
    },
    beforeDestroy: function () {
      window.removeEventListener('resize', this.handleWindowResize)
    },
    methods: {
      handleWindowResize (event) { this.drawSVG() },
      update: function () {
        this.drawSVG()
      },
      drawSVG: function () {
        const width = this.$el.clientWidth - margin.left - margin.right
        const height = this.$el.clientHeight - margin.top - margin.bottom
        this.svg
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
        const x = d3.scaleLinear().range([0, width])
        const y = d3.scaleLinear().range([height, 0])
        d3.axisLeft().scale(x)
        d3.axisTop().scale(y)
        x.domain(d3.extent(this.initialData['gg'], (d, i) => i))
        y.domain([0, 100]) // d3.max(this.initialData, d => d)])

        const createPath = d3.line()
          .x((d, i) => x(i))
          .y(d => y(d))
        const p = this.chartWrapper.selectAll('.p')
          .data(_.values(_.pick(this.initialData, this.catagories)))

        p.enter().append('path')
          .attr('class', 'p line')
          .attr('d', createPath)

        p.attr('d', createPath)

        p.exit().remove()

        const yAxis = d3.axisRight(y)
        // Add the y Axis
        this.chartWrapper.select('.y.axis')
          .call(yAxis)
      }
    }
  }
</script>
<style lang="scss">
  // svg {
    // margin: 25px;
  // }
  // path {
    // fill: none;
    // stroke: #76BF8A;
    // stroke-width: 3px;
  // }
  .line {
    fill: none;
    stroke: steelblue;
    stroke-width: 2px;
  }
  .svg-holder {
    height: 100%;
    margin: 0px;
  }
</style>
