
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
    
    this.chart = this.pie_chart_helper(this.$refs.canvas, this.frequency_data);
  },
  template: `
      <div class="row">
        <div class="col-xs-12">
          <h2 style="margin-top: 0;"> Task Frequency Charts </h2>
          
          
        </div>
        <div class="col-md-6 col-12">
          <div style="max-width:400px">
            <canvas ref="canvas"></canvas>
          </div>
        </div>
        
        <div class="col-md-6 col-12" v-if="frequency_data && Object.keys(frequency_data).length">
          <h4 class="mt-3">Task Frequency Details</h4>
          <div class="table-responsive">
            <table class="table table-bordered table-striped table-sm">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Frequency</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, label) in frequency_data" :key="label">
                  <td>{{ label }}</td>
                  <td>{{ value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        

      </div>
    
  `
};
