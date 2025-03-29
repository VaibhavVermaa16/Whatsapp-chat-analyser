import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
st.sidebar.title("Hello...!")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    try:
        # Read file as bytes
        bytes_data = uploaded_file.read()
        # Decode bytes to string
        data = bytes_data.decode("utf-8")
        df=preprocessor.preprocess(data)
        # Display the text data
    except UnicodeDecodeError as e:
        st.error(f"Decode Error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
    user_list=df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0,"Overall")
    
    selected_user=st.sidebar.selectbox("Show analysis for", user_list)
    helper.fetch_stats(selected_user,df)
    
    if st.sidebar.button("Show analysis"):
        # Display the stats
        st.title("Top Stats")
        col1, col2, col3, col4,col5=st.columns(5)
        with col1:
            st.header("Total Messages")
            num_messages=helper.fetch_stats(selected_user,df)
            st.title(num_messages)
        
        with col2:
            st.header("Total Words")
            num_words=helper.fetch_words(selected_user,df)
            st.title(num_words)
        
        with col3:
            st.header("Total Emojis")
            num_emojis, emojis = helper.fetch_emojis(selected_user, df)
            st.title(num_emojis)
            
            # Show emojis in a better way on the page
            st.text("Frequently used")
            emoji_html = " ".join([f"<span>{emoji}</span>" for emoji in emojis])
            st.markdown(f"<p style='font-size: 30px;'>{emoji_html}</p>", unsafe_allow_html=True)
        
            
        with col4:
            st.header("Total Media")
            media=helper.media_shared(selected_user,df)
            st.title(media)
        
        with col5:
            st.header("Total Links")
            urls=helper.links_shared(selected_user,df)
            st.title(urls)
            
        # Display the most busiest user in the chat (only applicable when group chat is there & only overall is selected)
        
        if selected_user=="Overall":
            st.header("Most busiest user")
            x, percent_data=helper.most_busy_user(df)
            
            names = x.index.tolist()
            counts = x.values.tolist()
            
            fig, axis=plt.subplots()
            
            col1, col2=st.columns(2)
            
            with col1:
                # Plotting
                fig, ax = plt.subplots()
                sns.barplot(x=names, y=counts, ax=ax, color='orange')
                plt.xticks(rotation=90)

                # Add value counts on top of bars
                for i, count in enumerate(counts):
                    ax.text(i, count + 0.05, str(count), ha='center', va='bottom')

                # Set labels and title
                ax.set_xlabel('Sender')
                ax.set_ylabel('Message Count')
                ax.set_title('Top Senders')

                # Display the plot in Streamlit
                st.pyplot(fig)
        
            with col2:
                st.header("Percentage of messages per user")
                st.table(percent_data)
        
        
        # Display the wordcloud
        st.title("Wordcloud")
        fig, ax=plt.subplots()
        wc_img=helper.create_wordcloud(selected_user,df)
        ax.imshow(wc_img)
        st.pyplot(fig)
        
        # Display the most frequent words
        st.title("Most frequent words")
        freq_words=helper.most_freq_words(selected_user,df)
        
        fig,ax=plt.subplots()
        ax.barh(freq_words['Word'], freq_words['count'])
        plt.xticks(rotation=90)
        st.pyplot(fig)
        
        # Display the timeline of messages
        
        # Monthly timeline
        st.title("Monthly timeline of messages")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['Message'], marker='o', color='r', linestyle='-', linewidth=2, markersize=6)
        plt.xticks(rotation='vertical')
        plt.xlabel("Time")
        plt.ylabel("Number of messages")
        st.pyplot(fig)
        
        # Daily timeline
        st.title("Daily timeline of messages")
        timeline=helper.daily_timeline(selected_user,df)
        fig,ax=plt.subplots(figsize=(12, 10))
        ax.plot(timeline['date'], timeline['Message'], color='b', linestyle='-')
        plt.xticks(rotation='vertical')
        plt.xlabel("Time")
        plt.ylabel("Number of messages")
        st.pyplot(fig)
         
        # # Activity map 
        st.title("Activity map")
        col1, col2=st.columns(2)
        with col1:
            st.header("Most active days")
            active_day=helper.week_activity_map(selected_user,df)
            fig,ax=plt.subplots()
            sns.barplot(x=active_day.index, y=active_day.values, ax=ax, color='purple')
            plt.xticks(rotation=90)
            st.pyplot(fig)
        
        with col2:
            st.header("Most active month")
            active_month=helper.month_activity_map(selected_user,df)
            fig,ax=plt.subplots()
            sns.barplot(x=active_month.index, y=active_month.values, ax=ax, color='green')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        # # Display the heatmap
        # st.title("Activity heatmap")
        # fig, ax=plt.subplots(figsize=(18, 10))
        # heatmap_data=helper.activity_heatmap(selected_user,df)
        # ax=sns.heatmap(heatmap_data.pivot_table(index='day_name', columns='Interval', values='Message', aggfunc='count').fillna(0), ax=ax)
        # st.pyplot(fig)
        