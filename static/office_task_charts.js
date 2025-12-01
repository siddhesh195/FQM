
export default {
  name: "FrequencyReportCharts",

  props: {
    frequency_data: {
      type: Object
    },
    office_name:{
        type: String
    },

    showSwalMessage: {
      type: Function
    },
    pie_chart_helper:{
        type: Function
    }
  },

  data() {
    return {
      chart:null
    };
  },

  methods: {
    
  },
  computed: {
    
  },
  watch:{
   
  },
  mounted() {
    console.log(this.frequency_data)
    console.log(this.office_name)
    console.log(this.pie_chart_helper)
    this.chart = this.pie_chart_helper(this.$refs.canvas, this.frequency_data);
  },
  template: `
      <div class="row">
        <div class="col-xs-12">
          <h2 style="margin-top: 0;"> Task Frequency Charts </h2>
          
          
        </div>

        <div style="max-width:400px">
            <canvas ref="canvas"></canvas>
        </div>

      </div>
    
  `
};
