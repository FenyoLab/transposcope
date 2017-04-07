<template>
  <table class="table is-narrow is-striped">
    <thead>
      <tr>
        <th v-for="key in columns"
          @click="sortBy(key)"
          :class="{ active: sortKey == key }">
          {{ key | capitalize }}
          <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
          </span>
        </th>
        <th>UCSC</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="entry in filteredData" @click="select(entry)">
        <td v-for="key in columns" :style="{color:entry[key][1]}">
          {{entry[key][0]}}
        </td>
        <td>🔗</td>
      </tr>
    </tbody>
  </table>
</template>

<script src="./site-table.js"></script>
<style src="./site-table.css"></style>
