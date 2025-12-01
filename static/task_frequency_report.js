
export default {
  name: "TaskFrequencyReport",

  props: {
    report_route_url: {
      type: String
    },
    showSwalMessage: {
      type: Function
    }
  },

  data() {
    return {
      selectedStartDate: null,
      selectedEndDate: null,
      reports: {},
      office_names: [],
      selectedOffice: ""
    };
  },

  methods: {
    fetch_reports() {
        // show in console type of showSwalMessage
 
        if (!this.selectedStartDate || !this.selectedEndDate) {
            this.showSwalMessage("Please select both start and end dates.");
            return;
        }
       
        axios.post(this.report_route_url, {
            
                start_date: this.selectedStartDate,
                end_date: this.selectedEndDate
            
        })
        .then(response => {
            // Handle the response data
            response.data;
           
            if (response.data.error){
                this.showSwalMessage(response.data.error);
                return;
            }
            this.reports = response.data;
            this.get_office_names();
            
        })
        .catch(err => {
            
        });

    },
    get_office_names() {
      this.office_names = Object.keys(this.reports);
    }
  },
  computed: {
    
  },
  watch:{
    selectedOffice(newOffice){
        //emit event to parent
        const data_to_send = {
            office: newOffice,
            report_data: this.reports[newOffice]
        }
        this.$emit('office-selected', data_to_send);
    }
  },
  mounted() {
 
  },
  template: `
      <div class="row">
        <div class="col-xs-12">
          <h2 style="margin-top: 0;"> Task Frequency Report </h2>
          <button class="btn btn-default btn-sm pull-right"
            @click="fetch_reports"
            v-if="!loading">
            Fetch Reports
          </button>
        </div>

        <label for="my-date">Pick a start date:</label>
        <input type="date" name="my-date" v-model="selectedStartDate">

        <label for="my-date">Pick a end date:</label>
        <input type="date"  name="my-date" v-model="selectedEndDate">

        <label>Select Office:</label>
        <select v-model="selectedOffice">
          <option disabled value="">Select office</option>
          <option v-for="office in office_names" :key="office" :value="office">
          {{ office }}
          </option>
        </select>
    
      </div>
    
  `
};
