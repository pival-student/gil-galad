Vue.component('attr-cp-btn', {
  props: {
    orthography: String
  },
  methods: {
    excludeItem: function () {
      this.$emit('exclude-item')
    },
    keepItem: function () {
      this.$emit('keep-item')
    },
  },
  template: '#attr-cp-temp'
})


const app = new Vue({
  el: '#app',
  data: {
    fileName: "copies.txt",
    exclude: [],
    keep: [],
    items: [],
  },
  created() {
    window.addEventListener('keydown', (e) => {
      if (e.code === "KeyA") {
        this.onExcludeItem(0);
      }
      if (e.code === "KeyD") {
        this.onKeepItem(0);
      }
    });
  },

  methods: {
    deleteItem: function (index) {
      this.items.splice(index, 1)

    },
    onKeepItem: function (index) {
      if (index >= 0 && index < this.items.length) {
        this.keep.push(this.items[index])
        this.deleteItem(index)
      }
    },
    onExcludeItem: function (index) {
      if (index >= 0 && index < this.items.length) {
        this.exclude.push(this.items[index])
        this.deleteItem(index)
      }
    },
    loadData: function (event) {
      this.items = []
      this.fileName = event.target.files[0].name
      event.target.files[0].text().then(txt => {
        const lines = txt.split("\n")
        for (let line of lines) {
          if (line.trim().length > 0) {
            let split = line.trim().split("\t")
            let item = []
              item.push(split[0])
            if (split.length > 1){
              item.push(split[1])
            } else {
              item.push("Example text unavailable")
            }
            this.items.push(item)
          }
        }
      })
    },
    saveAll: function () {
      this.saveData(this.exclude, "exclude.txt", false)
      this.saveData(this.keep, "keep.txt", false)
      this.saveData(this.items, "remaining.txt", true)
    },
    saveData: function (dat, name, both) {
      const blob = new Blob([this.getSaveString(dat, both)], {type: "text/plain"})
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = name
      link.click()
      URL.revokeObjectURL(link.href)
    },

    getSaveString: function (dat, both) {
      let strings = []
      for (let item of dat) {
        if (both){
          strings.push(item[0] + "\t" + item[1])
        } else {
          strings.push(item[0])
        }
      }
      return strings.join("\n")
    },
  },
  computed: {
    numItems: function () {
      return this.items.length
    },
    numKept: function () {
      return this.keep.length
    },
    numExcluded: function () {
      return this.exclude.length
    },
    current: function () {
      if (this.numItems > 0){
        return this.items[0][0]
      } else {
        return "No items loaded"
      }
    },
    currentExample: function () {
      if (this.numItems > 0){
        return this.items[0][1].replaceAll(this.items[0][0], "<mark>" + this.items[0][0] + "</mark>")
      } else {
        return "No items loaded"
      }
    }
  }
});

