import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.gluetypes import *
from awsgluedq.transforms import EvaluateDataQuality
from awsglue import DynamicFrame
import re

def _find_null_fields(ctx, schema, path, output, nullStringSet, nullIntegerSet, frame):
    if isinstance(schema, StructType):
        for field in schema:
            new_path = path + "." if path != "" else path
            output = _find_null_fields(ctx, field.dataType, new_path + field.name, output, nullStringSet, nullIntegerSet, frame)
    elif isinstance(schema, ArrayType):
        if isinstance(schema.elementType, StructType):
            output = _find_null_fields(ctx, schema.elementType, path, output, nullStringSet, nullIntegerSet, frame)
    elif isinstance(schema, NullType):
        output.append(path)
    else:
        x, distinct_set = frame.toDF(), set()
        for i in x.select(path).distinct().collect():
            distinct_ = i[path.split('.')[-1]]
            if isinstance(distinct_, list):
                distinct_set |= set([item.strip() if isinstance(item, str) else item for item in distinct_])
            elif isinstance(distinct_, str) :
                distinct_set.add(distinct_.strip())
            else:
                distinct_set.add(distinct_)
        if isinstance(schema, StringType):
            if distinct_set.issubset(nullStringSet):
                output.append(path)
        elif isinstance(schema, IntegerType) or isinstance(schema, LongType) or isinstance(schema, DoubleType):
            if distinct_set.issubset(nullIntegerSet):
                output.append(path)
    return output

def drop_nulls(glueContext, frame, nullStringSet, nullIntegerSet, transformation_ctx) -> DynamicFrame:
    nullColumns = _find_null_fields(frame.glue_ctx, frame.schema(), "", [], nullStringSet, nullIntegerSet, frame)
    return DropFields.apply(frame=frame, paths=nullColumns, transformation_ctx=transformation_ctx)

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node Amazon S3
AmazonS3_node1781162928182 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://careplus-data-demo-store/support-tickets/raw/"], "recurse": True}, transformation_ctx="AmazonS3_node1781162928182")

# Script generated for node Change Schema
ChangeSchema_node1781167103992 = ApplyMapping.apply(frame=AmazonS3_node1781162928182, mappings=[("ticket_id", "string", "ticket_id", "string"), ("created_at", "string", "created_at", "timestamp"), ("resolved_at", "string", "resolved_at", "timestamp"), ("agent", "string", "agent", "string"), ("priority", "string", "priority", "string"), ("num_interactions", "string", "num_interactions", "int"), ("issuecat", "string", "issuecat", "string"), ("channel", "string", "channel", "string"), ("status", "string", "status", "string"), ("agent_feedback", "string", "agent_feedback", "string")], transformation_ctx="ChangeSchema_node1781167103992")

# Script generated for node Drop Null Fields
DropNullFields_node1781167295528 = drop_nulls(glueContext, frame=ChangeSchema_node1781167103992, nullStringSet={""}, nullIntegerSet={}, transformation_ctx="DropNullFields_node1781167295528")

# Script generated for node Rename Field - issue category
RenameFieldissuecategory_node1781167466167 = RenameField.apply(frame=DropNullFields_node1781167295528, old_name="issuecat", new_name="issue_category", transformation_ctx="RenameFieldissuecategory_node1781167466167")

# Script generated for node Filter - num interactions
Filternuminteractions_node1781167575158 = Filter.apply(frame=RenameFieldissuecategory_node1781167466167, f=lambda row: (row["num_interactions"] >= 0), transformation_ctx="Filternuminteractions_node1781167575158")

# Script generated for node SQL Query - priority
SqlQuery0 = '''
select *,
    case
        When priority = 'Lw' THEN 'Low'
        When priority = 'Medum' THEN 'Medium'
        When priority = 'Hgh' THEN 'High'
    else priority
    end as priority
from myDataSource
'''
SQLQuerypriority_node1781167746830 = sparkSqlQuery(glueContext, query = SqlQuery0, mapping = {"myDataSource":Filternuminteractions_node1781167575158}, transformation_ctx = "SQLQuerypriority_node1781167746830")

# Script generated for node Amazon S3
EvaluateDataQuality().process_rows(frame=SQLQuerypriority_node1781167746830, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1781162925053", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
if (SQLQuerypriority_node1781167746830.count() >= 1):
   SQLQuerypriority_node1781167746830 = SQLQuerypriority_node1781167746830.coalesce(1)
AmazonS3_node1781168463333 = glueContext.write_dynamic_frame.from_options(frame=SQLQuerypriority_node1781167746830, connection_type="s3", format="glueparquet", connection_options={"path": "s3://careplus-data-demo-store/support-tickets/processed/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="AmazonS3_node1781168463333")

job.commit()