
export default {
  name: "TaskFrequencyReport",

  props: {
    report_route_url: {
      type: String
    },
    showSwalMessage: {
      type: Function
    },
    showToast: {
      type: Function
    },
    reports_fetched: {
      type: Object,
      default: null
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
            this.showToast("Reports fetched successfully.");
            this.reports = response.data;
            this.get_office_names();
            const data_to_send = {
              reports: this.reports,
              dates: {
                start_date: this.selectedStartDate,
                end_date: this.selectedEndDate
              }
            }
        
            this.$emit('reports-fetched', data_to_send);
            
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

    this.reports = this.reports_fetched || {};
    this.get_office_names();
  },
  template: `
    <div class="row task-frequency-report">
      <div class="col-xs-12 col-md-10 col-md-offset-1">

        <div class="panel panel-primary">
          <div class="panel-heading">
            <h3 class="panel-title">
              Task Frequency Report
            </h3>
          </div>

          <div class="panel-body">

          <p class="text-muted">
            Select a date range, fetch reports, and then choose an office.
          </p>

          <!-- Date selection -->
          <form class="form-horizontal">

            <div class="form-group">
              <label class="col-sm-3 control-label">
                Start Date
              </label>
              <div class="col-sm-9">
                <input
                  type="date"
                  class="form-control"
                  v-model="selectedStartDate"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="col-sm-3 control-label">
                End Date
              </label>
              <div class="col-sm-9">
                <input
                  type="date"
                  class="form-control"
                  v-model="selectedEndDate"
                >
              </div>
            </div>

            <!-- Fetch button -->
            <div class="form-group">
              <div class="col-sm-offset-3 col-sm-9">
                <button
                  type="button"
                  class="btn btn-primary"
                  @click="fetch_reports"
                >
                  Fetch Reports
                </button>
              </div>
            </div>

          </form>

          <hr>

          <!-- Office selection -->
          <div class="form-group">
            <label>
              Select Office
            </label>
            <select
              class="form-control"
              v-model="selectedOffice"
              :disabled="office_names.length === 0"
            >
              <option disabled value="">
                Select office
              </option>
              <option
                v-for="office in office_names"
                :key="office"
                :value="office"
              >
                {{ office }}
              </option>
            </select>
          </div>

        </div>

      </div>
    </div>
  </div>

    
  `
};
